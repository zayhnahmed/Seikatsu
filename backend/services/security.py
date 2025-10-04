"""
Security Service
Handles authentication, password hashing, JWT tokens, and user verification.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import logging

from models import User
from schemas import TokenData

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = "your-secret-key-here-change-in-production"  # CHANGE THIS IN PRODUCTION!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ==================== PASSWORD HASHING ====================

def hash_password(password: str) -> str:
    """
    Hash a plain password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# ==================== JWT TOKEN FUNCTIONS ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing the payload data (usually {"sub": username})
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData with username if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        
        if username is None:
            return None
        
        return TokenData(username=username)
        
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        return None


# ==================== USER AUTHENTICATION ====================

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username and password.
    
    Args:
        db: Database session
        username: Username or email
        password: Plain text password
        
    Returns:
        User object if authentication successful, None otherwise
    """
    # Try to find user by username or email
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        logger.warning(f"Authentication failed: User '{username}' not found")
        return None
    
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed: Invalid password for user '{username}'")
        return None
    
    logger.info(f"User '{username}' authenticated successfully")
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends()
) -> User:
    """
    Get the current authenticated user from JWT token.
    Use as a dependency in protected routes.
    
    Args:
        token: JWT token from request header
        db: Database session
        
    Returns:
        Current User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_access_token(token)
    
    if token_data is None or token_data.username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user (can be extended to check if user is disabled).
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        User object if active
        
    Raises:
        HTTPException: If user is inactive (requires is_active field in User model)
    """
    # Add this check if you have an is_active field in your User model:
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


# ==================== USER REGISTRATION ====================

def create_user(db: Session, username: str, email: str, password: str) -> User:
    """
    Create a new user with hashed password.
    
    Args:
        db: Database session
        username: Desired username
        email: User email
        password: Plain text password
        
    Returns:
        Created User object
        
    Raises:
        ValueError: If username or email already exists
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise ValueError(f"Username '{username}' already exists")
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise ValueError(f"Email '{email}' already registered")
    
    # Create new user with hashed password
    hashed_password = hash_password(password)
    
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user created: {username}")
    
    return new_user


# ==================== PASSWORD RESET & CHANGE ====================

def change_password(
    db: Session,
    user_id: int,
    old_password: str,
    new_password: str
) -> bool:
    """
    Change user password (requires old password verification).
    
    Args:
        db: Database session
        user_id: User ID
        old_password: Current password
        new_password: New password
        
    Returns:
        True if password changed successfully
        
    Raises:
        ValueError: If old password is incorrect
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise ValueError("User not found")
    
    # Verify old password
    if not verify_password(old_password, user.hashed_password):
        raise ValueError("Current password is incorrect")
    
    # Update to new password
    user.hashed_password = hash_password(new_password)
    db.commit()
    
    logger.info(f"Password changed for user {user.username}")
    
    return True


def reset_password(db: Session, user_id: int, new_password: str) -> bool:
    """
    Reset user password (admin function, no old password required).
    Use with caution - should be paired with email verification.
    
    Args:
        db: Database session
        user_id: User ID
        new_password: New password
        
    Returns:
        True if password reset successfully
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise ValueError("User not found")
    
    user.hashed_password = hash_password(new_password)
    db.commit()
    
    logger.info(f"Password reset for user {user.username}")
    
    return True


# ==================== TOKEN REFRESH ====================

def create_refresh_token(data: dict) -> str:
    """
    Create a refresh token with longer expiration.
    
    Args:
        data: Dictionary containing the payload data
        
    Returns:
        Encoded refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # Refresh token lasts 7 days
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Generate a new access token from a valid refresh token.
    
    Args:
        refresh_token: JWT refresh token
        
    Returns:
        New access token if refresh token is valid, None otherwise
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "refresh":
            return None
        
        username: Optional[str] = payload.get("sub")
        if username is None:
            return None
        
        # Create new access token
        access_token = create_access_token(data={"sub": username})
        return access_token
        
    except JWTError:
        return None


# ==================== EMAIL VERIFICATION ====================

def create_verification_token(email: str) -> str:
    """
    Create an email verification token.
    
    Args:
        email: User email
        
    Returns:
        Verification token string
    """
    expire = datetime.utcnow() + timedelta(hours=24)  # Valid for 24 hours
    to_encode = {"sub": email, "exp": expire, "type": "verification"}
    
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_email_token(token: str) -> Optional[str]:
    """
    Verify an email verification token.
    
    Args:
        token: Verification token
        
    Returns:
        Email if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "verification":
            return None
        
        email: Optional[str] = payload.get("sub")
        return email
        
    except JWTError:
        return None


# ==================== UTILITY FUNCTIONS ====================

def is_strong_password(password: str) -> tuple[bool, str]:
    """
    Check if password meets strength requirements.
    
    Args:
        password: Password to check
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter"
    
    return True, "Password is strong"


def sanitize_username(username: str) -> str:
    """
    Sanitize username (remove special characters, convert to lowercase).
    
    Args:
        username: Raw username
        
    Returns:
        Sanitized username
    """
    # Remove special characters, keep only alphanumeric and underscore
    sanitized = ''.join(c for c in username if c.isalnum() or c == '_')
    return sanitized.lower()


# ==================== SETUP INSTRUCTIONS ====================

"""
IMPORTANT SETUP STEPS:

1. Install required packages:
   pip install python-jose[cryptography] passlib[bcrypt] python-multipart

2. Generate a secure SECRET_KEY for production:
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   Replace SECRET_KEY at the top of this file with the generated key.

3. Update your database.py to provide the get_db dependency:
   
   from sqlalchemy.orm import Session
   from database import SessionLocal
   
   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()

4. Example usage in routes:

   from fastapi import APIRouter, Depends
   from services.security import get_current_user, create_access_token, authenticate_user
   from models import User
   
   router = APIRouter()
   
   @router.post("/login")
   def login(username: str, password: str, db: Session = Depends(get_db)):
       user = authenticate_user(db, username, password)
       if not user:
           raise HTTPException(status_code=401, detail="Invalid credentials")
       
       access_token = create_access_token(data={"sub": user.username})
       return {"access_token": access_token, "token_type": "bearer"}
   
   @router.get("/me")
   def read_users_me(current_user: User = Depends(get_current_user)):
       return current_user

5. Protect routes by adding dependency:
   @router.get("/protected")
   def protected_route(current_user: User = Depends(get_current_user)):
       return {"message": f"Hello {current_user.username}"}
"""