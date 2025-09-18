"""
Dependencies for Seikatsu Backend
Contains database session management and authentication dependencies
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
import crud
import schemas
from database import SessionLocal
from config import settings

# Security scheme for JWT
security = HTTPBearer()

def get_db():
    """
    Database session dependency
    Creates a new database session for each request and closes it when done
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> schemas.User:
    """
    Dependency to get the current authenticated user from JWT token
    
    Args:
        credentials: JWT token from Authorization header
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Get user from database
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    
    return user

def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user)
) -> schemas.User:
    """
    Dependency to get current active user (for future user status checks)
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is inactive (placeholder for future implementation)
    """
    # Placeholder for future user status checks (e.g., banned, suspended)
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user

# Optional dependency - allows both authenticated and anonymous access
def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> schemas.User | None:
    """
    Optional authentication dependency
    Returns user if authenticated, None if not
    Useful for endpoints that work for both authenticated and anonymous users
    """
    if not credentials:
        return None
        
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None

def get_admin_user(
    current_user: schemas.User = Depends(get_current_user)
) -> schemas.User:
    """
    Dependency for admin-only endpoints (placeholder for future implementation)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Admin user
        
    Raises:
        HTTPException: If user is not an admin
    """
    # Placeholder for admin role checking
    # This would check if user has admin role in the future
    # if not current_user.is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin access required"
    #     )
    
    return current_user

def validate_user_owns_resource(
    resource_user_id: int,
    current_user: schemas.User = Depends(get_current_user)
) -> bool:
    """
    Utility dependency to validate user owns a resource
    
    Args:
        resource_user_id: User ID that owns the resource
        current_user: Current authenticated user
        
    Returns:
        True if user owns the resource
        
    Raises:
        HTTPException: If user doesn't own the resource
    """
    if resource_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't own this resource"
        )
    return True

# Database utility functions that can be used as dependencies
def get_db_with_autocommit():
    """
    Database session with autocommit for specific use cases
    Use with caution - prefer get_db() for most operations
    """
    db = SessionLocal()
    db.autocommit = True
    try:
        yield db
    finally:
        db.close()

def get_db_with_rollback():
    """
    Database session that automatically rolls back on any exception
    Useful for operations that should not persist if anything fails
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()