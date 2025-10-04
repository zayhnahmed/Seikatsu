"""
XP Manager Service
Handles all XP, leveling, and progression logic for Seikatsu.
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Tuple
import logging
from models import Level, UserStats, User, Category
from schemas import LevelProgress

# Configure logging
logger = logging.getLogger(__name__)

# XP Configuration - Exponential leveling curve
XP_BASE = 100  # XP needed for level 2
XP_MULTIPLIER = 1.5  # Exponential growth factor

# XP Rewards Configuration
XP_REWARDS = {
    "journal_entry": 20,
    "task_completion": 10,
    "daily_streak": 5,
    "weekly_goal": 50,
    "monthly_goal": 200,
}


def calculate_level(xp: int) -> int:
    """
    Calculate the level based on total XP using exponential curve.
    
    Formula: level = floor(log(xp / XP_BASE + 1) / log(XP_MULTIPLIER)) + 1
    
    Args:
        xp: Total experience points
        
    Returns:
        Current level number (minimum 1)
    """
    if xp <= 0:
        return 1
    
    level = 1
    xp_needed = XP_BASE
    
    while xp >= xp_needed:
        xp -= xp_needed
        level += 1
        xp_needed = int(XP_BASE * (XP_MULTIPLIER ** (level - 1)))
    
    return level


def get_xp_for_level(level: int) -> int:
    """
    Calculate total XP required to reach a specific level.
    
    Args:
        level: Target level number
        
    Returns:
        Total XP required to reach that level
    """
    if level <= 1:
        return 0
    
    total_xp = 0
    for lvl in range(1, level):
        total_xp += int(XP_BASE * (XP_MULTIPLIER ** (lvl - 1)))
    
    return total_xp


def get_xp_for_next_level(current_level: int) -> int:
    """
    Calculate XP needed for the next level.
    
    Args:
        current_level: Current level number
        
    Returns:
        XP required for next level
    """
    return int(XP_BASE * (XP_MULTIPLIER ** (current_level - 1)))


def calculate_level_progress(xp: int) -> LevelProgress:
    """
    Calculate detailed level progression information.
    
    Args:
        xp: Total experience points
        
    Returns:
        LevelProgress schema with detailed progression data
    """
    current_level = calculate_level(xp)
    current_level_threshold = get_xp_for_level(current_level)
    next_level_threshold = get_xp_for_level(current_level + 1)
    
    progress_in_current_level = xp - current_level_threshold
    xp_needed_for_next_level = next_level_threshold - xp
    progress_percentage = (progress_in_current_level / (next_level_threshold - current_level_threshold)) * 100
    
    return LevelProgress(
        current_level=current_level,
        total_xp=xp,
        progress_in_current_level=progress_in_current_level,
        xp_needed_for_next_level=xp_needed_for_next_level,
        progress_percentage=round(progress_percentage, 2),
        current_level_threshold=current_level_threshold,
        next_level_threshold=next_level_threshold,
    )


def check_level_up(old_xp: int, new_xp: int) -> Tuple[bool, int, int]:
    """
    Check if adding XP causes a level up.
    
    Args:
        old_xp: XP before addition
        new_xp: XP after addition
        
    Returns:
        Tuple of (leveled_up: bool, old_level: int, new_level: int)
    """
    old_level = calculate_level(old_xp)
    new_level = calculate_level(new_xp)
    
    return new_level > old_level, old_level, new_level


def add_xp(
    db: Session,
    user_id: int,
    category_id: int,
    amount: int,
    reason: Optional[str] = None
) -> Dict:
    """
    Add XP to a specific category and check for level-up.
    Also updates overall user stats.
    
    Args:
        db: Database session
        user_id: User ID
        category_id: Category ID to add XP to
        amount: Amount of XP to add
        reason: Optional reason for XP gain (for logging)
        
    Returns:
        Dictionary with level up info and updated stats
    """
    try:
        # Get or create category level
        category_level = db.query(Level).filter(
            Level.user_id == user_id,
            Level.category_id == category_id
        ).first()
        
        if not category_level:
            # Create new level entry for this category
            category_level = Level(
                user_id=user_id,
                category_id=category_id,
                level=1,
                xp=0
            )
            db.add(category_level)
        
        # Store old XP for level check
        old_xp = category_level.xp
        
        # Add XP
        category_level.xp += amount
        new_xp = category_level.xp
        
        # Check for level up
        leveled_up, old_level, new_level = check_level_up(old_xp, new_xp)
        
        if leveled_up:
            category_level.level = new_level
            logger.info(
                f"User {user_id} leveled up in category {category_id}: "
                f"Level {old_level} -> {new_level}"
            )
        
        # Update overall user stats
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        
        if not user_stats:
            # Create user stats if doesn't exist
            user_stats = UserStats(user_id=user_id, level=1, total_xp=0)
            db.add(user_stats)
        
        # Update total XP
        old_total_xp = user_stats.total_xp
        user_stats.total_xp += amount
        new_total_xp = user_stats.total_xp
        
        # Check for overall level up
        overall_leveled_up, old_overall_level, new_overall_level = check_level_up(
            old_total_xp, new_total_xp
        )
        
        if overall_leveled_up:
            user_stats.level = new_overall_level
            logger.info(
                f"User {user_id} overall level up: "
                f"Level {old_overall_level} -> {new_overall_level}"
            )
        
        db.commit()
        db.refresh(category_level)
        db.refresh(user_stats)
        
        logger.info(
            f"Added {amount} XP to user {user_id} in category {category_id}. "
            f"Reason: {reason or 'N/A'}"
        )
        
        return {
            "success": True,
            "xp_added": amount,
            "category_level": category_level.level,
            "category_xp": category_level.xp,
            "category_leveled_up": leveled_up,
            "old_category_level": old_level if leveled_up else None,
            "new_category_level": new_level if leveled_up else None,
            "total_xp": user_stats.total_xp,
            "overall_level": user_stats.level,
            "overall_leveled_up": overall_leveled_up,
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding XP for user {user_id}: {str(e)}")
        raise


def deduct_xp(
    db: Session,
    user_id: int,
    category_id: int,
    amount: int,
    reason: Optional[str] = None
) -> Dict:
    """
    Deduct XP from a specific category (e.g., for marketplace purchases).
    Prevents XP from going below 0.
    
    Args:
        db: Database session
        user_id: User ID
        category_id: Category ID to deduct XP from
        amount: Amount of XP to deduct
        reason: Optional reason for XP deduction (for logging)
        
    Returns:
        Dictionary with updated stats
    """
    try:
        # Get category level
        category_level = db.query(Level).filter(
            Level.user_id == user_id,
            Level.category_id == category_id
        ).first()
        
        if not category_level:
            raise ValueError(f"No level found for category {category_id}")
        
        # Ensure XP doesn't go below 0
        old_xp = category_level.xp
        category_level.xp = max(0, category_level.xp - amount)
        actual_deduction = old_xp - category_level.xp
        
        # Recalculate level
        category_level.level = calculate_level(category_level.xp)
        
        # Update overall user stats
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        
        if user_stats:
            old_total_xp = user_stats.total_xp
            user_stats.total_xp = max(0, user_stats.total_xp - actual_deduction)
            user_stats.level = calculate_level(user_stats.total_xp)
        
        db.commit()
        db.refresh(category_level)
        if user_stats:
            db.refresh(user_stats)
        
        logger.info(
            f"Deducted {actual_deduction} XP from user {user_id} in category {category_id}. "
            f"Reason: {reason or 'N/A'}"
        )
        
        return {
            "success": True,
            "xp_deducted": actual_deduction,
            "category_level": category_level.level,
            "category_xp": category_level.xp,
            "total_xp": user_stats.total_xp if user_stats else 0,
            "overall_level": user_stats.level if user_stats else 1,
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deducting XP for user {user_id}: {str(e)}")
        raise


def get_user_level_details(db: Session, user_id: int) -> Dict:
    """
    Get comprehensive level details for a user across all categories.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dictionary with overall stats and per-category breakdowns
    """
    try:
        # Get overall user stats
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        
        if not user_stats:
            return {
                "overall": {
                    "level": 1,
                    "total_xp": 0,
                    "progress": calculate_level_progress(0).dict()
                },
                "categories": []
            }
        
        # Get category levels
        category_levels = db.query(Level).filter(Level.user_id == user_id).all()
        
        categories = []
        for cat_level in category_levels:
            category = db.query(Category).filter(Category.id == cat_level.category_id).first()
            categories.append({
                "category_id": cat_level.category_id,
                "category_name": category.name if category else "Unknown",
                "level": cat_level.level,
                "xp": cat_level.xp,
                "progress": calculate_level_progress(cat_level.xp).dict()
            })
        
        return {
            "overall": {
                "level": user_stats.level,
                "total_xp": user_stats.total_xp,
                "progress": calculate_level_progress(user_stats.total_xp).dict()
            },
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Error getting level details for user {user_id}: {str(e)}")
        raise