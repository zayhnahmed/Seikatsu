"""
Database Seeding Script
Populates the database with default categories and optional test data.
Run this after initial database setup to initialize essential data.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

from database import SessionLocal
from models import Category, User, UserStats
from config import DEFAULT_CATEGORIES
from crud import get_password_hash
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def seed_categories():
    """
    Seed default categories into the database.
    Skips categories that already exist to prevent duplicates.
    """
    db = SessionLocal()
    
    try:
        logger.info("Starting category seeding...")
        
        # Check if categories already exist
        existing_count = db.query(Category).count()
        
        if existing_count > 0:
            logger.info(f"Categories already exist ({existing_count} found). Skipping seed.")
            return
        
        # Add each default category
        added_count = 0
        for cat_data in DEFAULT_CATEGORIES:
            # Double-check individual category doesn't exist
            existing = db.query(Category).filter(
                Category.name == cat_data["name"]
            ).first()
            
            if not existing:
                category = Category(name=cat_data["name"])
                db.add(category)
                added_count += 1
                logger.info(f"Added category: {cat_data['name']}")
        
        # Commit all categories at once
        db.commit()
        logger.info(f"✅ Successfully seeded {added_count} categories!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error seeding categories: {str(e)}")
        raise
    finally:
        db.close()


def seed_test_user():
    """
    Create a test user for development/testing purposes.
    Only creates the user if it doesn't already exist.
    """
    db = SessionLocal()
    
    try:
        logger.info("Checking for test user...")
        
        # Check if test user already exists
        existing_user = db.query(User).filter(
            User.username == "testuser"
        ).first()
        
        if existing_user:
            logger.info("Test user already exists. Skipping creation.")
            return
        
        # Create test user
        test_user = User(
            username="testuser",
            email="test@seikatsu.app",
            hashed_password=get_password_hash("testpass123")
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create initial user stats
        user_stats = UserStats(
            user_id=test_user.id,
            level=1,
            total_xp=0
        )
        db.add(user_stats)
        db.commit()
        
        logger.info(f"✅ Test user created successfully! Username: testuser, Password: testpass123")
        logger.info(f"   User ID: {test_user.id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creating test user: {str(e)}")
        raise
    finally:
        db.close()


def seed_all():
    """
    Run all seeding operations in sequence.
    """
    logger.info("=" * 60)
    logger.info("SEIKATSU DATABASE SEEDING")
    logger.info("=" * 60)
    
    try:
        # Seed categories
        seed_categories()
        
        # Seed test user (optional - only in development)
        from config import settings
        if settings.is_development:
            seed_test_user()
        else:
            logger.info("Skipping test user creation (not in development mode)")
        
        logger.info("=" * 60)
        logger.info("✅ Database seeding completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ Database seeding failed: {str(e)}")
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    seed_all()