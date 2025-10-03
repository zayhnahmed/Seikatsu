"""
Authentication Routes
Handles user registration, login, and JWT token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
import crud, schemas
from database import get_db
from logger import logger

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ===================== #
#  AUTHENTICATION ENDPOINTS
# ===================== #

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account
    
    - **username**: Unique username (3-50 chars)
    - **email**: Valid email address
    - **password**: Minimum 6 characters
    
    Returns created user object with initial stats (Level 1, 0 XP)
    """
    try:
        db_user = crud.create_user(db, user)
        logger.info(f"New user registered: {db_user.username}")
        return db_user
    except ValueError as e:
        # Handle duplicate username/email
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=schemas.Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    User login with username and password
    
    Returns JWT access token for authenticated requests
    
    - **username**: User's username
    - **password**: User's password
    """
    # Authenticate user
    user = crud.get_user_by_username(db, form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify password
    if not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # TODO: Generate JWT token using services.auth_service
    # For now, return user_id as token (replace with actual JWT implementation)
    access_token = f"user_{user.id}_token"  # Placeholder
    
    logger.info(f"User logged in: {user.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=schemas.UserWithStats)
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get currently authenticated user's profile
    
    Requires valid JWT token in Authorization header
    
    Returns user details with current level and XP stats
    """
    # TODO: Decode JWT token to get user_id
    # For now, extract user_id from placeholder token
    try:
        user_id = int(token.split("_")[1])
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user stats
    user_stats = crud.get_user_stats(db, user_id)
    if not user_stats:
        user_stats = crud.create_user_stats(db, user_id)
    
    return schemas.UserWithStats.model_validate({
        **user.__dict__,
        "user_stats": user_stats
    })


@router.post("/logout")
def logout_user(token: str = Depends(oauth2_scheme)):
    """
    User logout (token invalidation)
    
    Note: With JWT, logout is typically handled client-side by discarding the token
    Server-side token blacklisting can be implemented for enhanced security
    """
    # TODO: Implement token blacklisting if needed
    logger.info("User logged out")
    return {"message": "Successfully logged out"}


# ===================== #
#  UTILITY FUNCTIONS
# ===================== #

async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> int:
    """
    Dependency to extract and validate current user ID from token
    Use this in other routes that require authentication
    """
    try:
        # TODO: Replace with actual JWT decoding
        user_id = int(token.split("_")[1])
        user = crud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user_id
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )