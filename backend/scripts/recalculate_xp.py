# scripts/recalculate_xp.py

"""
XP Recalculation Script
Recalculates XP and levels for all users when XP formulas or leveling logic changes.
Useful for maintenance after updating the XP system.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

from database import SessionLocal
from models import User, UserStats, Level
from services.xp_manager import calculate_level, get_xp_for_level
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def recalculate_user_xp(db, user_id: int):
    """
    Recalculate XP and level for a specific user.
    
    Args:
        db: Database session
        user_id: User ID to recalculate
    """
    try:
        # Get user stats
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        
        if not user_stats:
            logger.warning(f"No stats found for user {user_id}, skipping")
            return False
        
        # Recalculate level based on current total XP
        old_level = user_stats.level
        new_level = calculate_level(user_stats.total_xp)
        
        # Update level if changed
        if old_level != new_level:
            user_stats.level = new_level
            logger.info(f"User {user_id}: Level updated {old_level} -> {new_level}")
        
        # Recalculate category levels
        category_levels = db.query(Level).filter(Level.user_id == user_id).all()
        
        for cat_level in category_levels:
            old_cat_level = cat_level.level
            new_cat_level = calculate_level(cat_level.xp)
            
            if old_cat_level != new_cat_level:
                cat_level.level = new_cat_level
                logger.info(
                    f"User {user_id}, Category {cat_level.category_id}: "
                    f"Level updated {old_cat_level} -> {new_cat_level}"
                )
        
        db.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error recalculating XP for user {user_id}: {str(e)}")
        db.rollback()
        return False


def recalculate_all_users():
    """
    Recalculate XP and levels for all users in the database.
    """
    db = SessionLocal()
    
    try:
        logger.info("=" * 60)
        logger.info("SEIKATSU XP RECALCULATION")
        logger.info("=" * 60)
        
        # Get all users
        users = db.query(User).all()
        total_users = len(users)
        
        if total_users == 0:
            logger.warning("No users found in database")
            return
        
        logger.info(f"Found {total_users} users to process")
        logger.info("-" * 60)
        
        success_count = 0
        error_count = 0
        
        # Process each user
        for idx, user in enumerate(users, 1):
            logger.info(f"Processing user {idx}/{total_users}: {user.username} (ID: {user.id})")
            
            if recalculate_user_xp(db, user.id):
                success_count += 1
            else:
                error_count += 1
        
        # Summary
        logger.info("=" * 60)
        logger.info("RECALCULATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Users: {total_users}")
        logger.info(f"Successfully Recalculated: {success_count}")
        logger.info(f"Errors: {error_count}")
        
        if error_count == 0:
            logger.info("✅ All users recalculated successfully!")
        else:
            logger.warning(f"⚠️  Completed with {error_count} errors")
        
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Fatal error during recalculation: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


def recalculate_single_user(user_id: int):
    """
    Recalculate XP for a single user by ID.
    
    Args:
        user_id: User ID to recalculate
    """
    db = SessionLocal()
    
    try:
        logger.info(f"Recalculating XP for user {user_id}...")
        
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.error(f"❌ User {user_id} not found")
            return
        
        logger.info(f"Found user: {user.username}")
        
        if recalculate_user_xp(db, user_id):
            logger.info(f"✅ Successfully recalculated XP for user {user_id}")
        else:
            logger.error(f"❌ Failed to recalculate XP for user {user_id}")
            
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Recalculate specific user
        try:
            user_id = int(sys.argv[1])
            recalculate_single_user(user_id)
        except ValueError:
            logger.error("Invalid user ID provided. Please provide a numeric user ID.")
            sys.exit(1)
    else:
        # Recalculate all users
        recalculate_all_users()