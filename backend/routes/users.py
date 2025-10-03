"""
User Routes
Handles user profile, stats, and XP/level management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import crud, schemas
from database import get_db
from logger import logger
from .auth import get_current_user_id

router = APIRouter()

# ===================== #
#  USER PROFILE ENDPOINTS
# ===================== #

@router.get("/me", response_model=schemas.UserWithStats)
def get_my_profile(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile with stats
    
    Returns user info along with level and XP information
    """
    try:
        user = crud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_stats = crud.get_user_stats(db, user_id)
        if not user_stats:
            user_stats = crud.create_user_stats(db, user_id)
        
        return schemas.UserWithStats.model_validate({
            **user.__dict__,
            "user_stats": user_stats
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.get("/{user_id}", response_model=schemas.User)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get public user profile by ID
    
    Returns basic user information (no sensitive data)
    """
    try:
        user = crud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )


# ===================== #
#  USER STATS ENDPOINTS
# ===================== #

@router.get("/stats/xp", response_model=schemas.UserStats)
def get_user_xp_stats(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get user's XP and level statistics
    
    Returns current level and total XP earned
    """
    try:
        stats = crud.get_user_stats(db, user_id)
        if not stats:
            stats = crud.create_user_stats(db, user_id)
        return stats
    except Exception as e:
        logger.error(f"Error fetching user stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user stats"
        )


@router.get("/stats/level-progress", response_model=schemas.LevelProgress)
def get_level_progress(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get detailed level progression information
    
    Returns:
    - Current level
    - Total XP
    - XP progress in current level
    - XP needed for next level
    - Progress percentage
    - Level thresholds
    """
    try:
        progress = crud.get_level_progress(db, user_id)
        return progress
    except Exception as e:
        logger.error(f"Error fetching level progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve level progress"
        )


@router.get("/stats/activity", response_model=schemas.ActivityStats)
def get_activity_statistics(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive user activity statistics
    
    Returns:
    - Total journal entries
    - Total tasks
    - Completed tasks count
    - Task completion rate
    - Current level and XP
    """
    try:
        stats = crud.get_user_activity_stats(db, user_id)
        return stats
    except Exception as e:
        logger.error(f"Error fetching activity stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activity statistics"
        )


@router.get("/stats/recent-activity", response_model=schemas.RecentActivity)
def get_recent_user_activity(
    days: int = Query(7, ge=1, le=365, description="Number of days to look back"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get recent user activity over specified period
    
    Returns journals and completed tasks from the last N days
    Default: last 7 days
    """
    try:
        activity = crud.get_recent_activity(db, user_id, days=days)
        return activity
    except Exception as e:
        logger.error(f"Error fetching recent activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent activity"
        )


# ===================== #
#  XP MANAGEMENT ENDPOINTS
# ===================== #

@router.post("/xp/reset", response_model=schemas.UserStats)
def reset_xp(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Reset user's XP and level to initial state
    
    WARNING: This action resets level to 1 and XP to 0
    Use for testing or special events only
    """
    try:
        stats = crud.reset_user_xp(db, user_id)
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User stats not found"
            )
        logger.warning(f"User {user_id} XP and level have been reset")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting XP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset XP"
        )


@router.post("/xp/add", response_model=schemas.UserStats)
def add_manual_xp(
    xp_amount: int = Query(..., ge=1, le=10000, description="XP amount to add"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Manually add XP to user (admin/testing feature)
    
    Adds specified XP and recalculates level
    """
    try:
        stats = crud.update_user_xp(db, user_id, xp_amount)
        logger.info(f"Manually added {xp_amount} XP to user {user_id}")
        return stats
    except Exception as e:
        logger.error(f"Error adding manual XP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add XP"
        )