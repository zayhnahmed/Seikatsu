"""
Authentication Routes
Handles user registration, login, and JWT token management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
import crud
import schemas
from deps import get_db
from config import settings
import jwt
from datetime import datetime, timezone

router = APIRouter()
security = HTTPBearer()

# JWT Token utilities
def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials, db: Session):
    """Verify JWT token and return user"""
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/signup", response_model=schemas.MessageResponse)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """User registration"""
    try:
        user = crud.create_user(db, user=user_data)
        return schemas.MessageResponse(
            message="User created successfully",
            detail=f"Welcome {user.username}! You can now login to get your access token."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@router.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """User login - returns JWT access token"""
    user = crud.get_user_by_username(db, username=user_credentials.username)
    
    if not user or not crud.verify_password(user_credentials.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }

@router.post("/refresh")
def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    user = verify_token(credentials, db)
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/me", response_model=schemas.User)
def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user from JWT token"""
    return verify_token(credentials, db)

@router.post("/logout")
def logout():
    """Logout user (client-side token removal)"""
    return {
        "message": "Successfully logged out",
        "detail": "Please remove the token from your client storage"
    }

@router.post("/change-password")
def change_password(
    password_change: schemas.PasswordChange,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Change user password"""
    current_user = verify_token(credentials, db)
    
    # Verify current password
    if not crud.verify_password(password_change.current_password, str(current_user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    try:
        crud.update_user_password(db, user_id=current_user.id, new_password=password_change.new_password)
        return {"message": "Password updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating password: {str(e)}")

@router.post("/request-password-reset")
def request_password_reset(email: str, db: Session = Depends(get_db)):
    """Request password reset (placeholder for future email implementation)"""
    user = crud.get_user_by_email(db, email=email)
    if not user:
        # Don't reveal if email exists for security
        return {"message": "If the email exists, you will receive password reset instructions"}
    
    # TODO: Implement email sending logic
    return {
        "message": "Password reset functionality coming soon!",
        "detail": "Email integration will be added in future version"
    }

@router.get("/verify-token")
def verify_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Verify if token is valid"""
    try:
        user = verify_token(credentials, db)
        return {
            "valid": True,
            "user_id": user.id,
            "username": user.username,
            "message": "Token is valid"
        }
    except HTTPException:
        return {
            "valid": False,
            "message": "Token is invalid or expired"
        }