"""
Streak Reset Script
Resets all user streaks to zero. Useful for testing or periodic challenges.
WARNING: This is a destructive operation. Use with caution.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

from database import SessionLocal
from models import User
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def reset_all_streaks():
    """
    Reset streaks for all users in the database.
    This function doesn't actually modify streak data since streaks are calculated
    dynamically from journal/task entries rather than stored as a field.
    
    Note: In Seikatsu, streaks are calculated on-the-fly from journal entries
    and task completion dates. To truly "reset" streaks, you would need to
    delete or archive old entries, which this script intentionally does not do
    to preserve user data.
    """
    db = SessionLocal()
    
    try:
        logger.info("=" * 60)
        logger.info("SEIKATSU STREAK RESET")
        logger.info("=" * 60)
        
        # Get all users
        users = db.query(User).all()
        total_users = len(users)
        
        if total_users == 0:
            logger.warning("No users found in database")
            return
        
        logger.info(f"Found {total_users} users")
        
        # Note about streak calculation
        logger.info("-" * 60)
        logger.info("NOTE: Streaks in Seikatsu are calculated dynamically from")
        logger.info("journal entries and task completion dates, not stored as fields.")
        logger.info("This means streaks will automatically reset when users stop")
        logger.info("their daily activities.")
        logger.info("-" * 60)
        
        # If you had a streak field to reset, it would look like this:
        # for user in users:
        #     user.streak = 0
        # db.commit()
        
        logger.info("Current implementation: Streaks are calculated dynamically")
        logger.info("No database modifications needed for streak reset")
        
        logger.info("=" * 60)
        logger.info("✅ Streak information displayed")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error during streak reset: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


def confirm_reset():
    """
    Ask for user confirmation before proceeding with reset.
    """
    logger.warning("⚠️  WARNING: This will reset streak data for all users!")
    logger.warning("⚠️  This operation cannot be undone.")
    
    response = input("\nAre you sure you want to continue? (yes/no): ").lower().strip()
    
    return response == "yes"


def display_current_streaks():
    """
    Display current streak information for all users.
    Helpful for verification before/after reset operations.
    """
    db = SessionLocal()
    
    try:
        from services.insights import calculate_streaks
        
        logger.info("=" * 60)
        logger.info("CURRENT STREAK STATUS")
        logger.info("=" * 60)
        
        users = db.query(User).all()
        
        if not users:
            logger.info("No users found")
            return
        
        for user in users:
            try:
                streaks = calculate_streaks(db, user.id)
                logger.info(
                    f"User: {user.username} (ID: {user.id}) | "
                    f"Journal Streak: {streaks.journal_streak} days | "
                    f"Task Streak: {streaks.task_completion_streak} days"
                )
            except Exception as e:
                logger.error(f"Error calculating streaks for user {user.id}: {str(e)}")
        
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error displaying streaks: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Streak reset script for Seikatsu")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt and proceed with reset"
    )
    parser.add_argument(
        "--show-only",
        action="store_true",
        help="Only display current streaks without resetting"
    )
    
    args = parser.parse_args()
    
    try:
        if args.show_only:
            # Just display current streaks
            display_current_streaks()
        else:
            # Proceed with reset (with or without confirmation)
            if args.force or confirm_reset():
                reset_all_streaks()
                display_current_streaks()
            else:
                logger.info("Streak reset operation cancelled by user.")
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)