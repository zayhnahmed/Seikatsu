import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from urllib.parse import quote_plus

# =========================
#  DATABASE URL - Updated for PostgreSQL with proper encoding
# =========================
def get_database_url():
    """Get database URL from environment variables with proper password encoding"""
    # Use environment variables for security
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "Ahmed@5977")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5452")
    db_name = os.getenv("DB_NAME", "postgres")
    
    # URL encode the password to handle special characters
    encoded_password = quote_plus(db_password)
    
    return f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"

DATABASE_URL = get_database_url()

# =========================
#  ENGINE & SESSION
# =========================
engine = create_engine(DATABASE_URL, echo=False)  # Set echo=True for SQL debugging

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models - this needs to be defined BEFORE importing models
Base = declarative_base()

# =========================
#  UTILITY FUNCTION
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
#  INITIALIZE DB & DEFAULT CATEGORIES
# =========================
def init_db():
    """Initialize database with tables and default categories"""
    # Import models here to avoid circular imports
    from models import Category
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created!")
    
    # Default categories for Seikatsu
    default_categories = [
        {"name": "Strength"},
        {"name": "Learning"}, 
        {"name": "Relationship"},
        {"name": "Spirituality"},
        {"name": "Career"},
        {"name": "Sleep"},
        {"name": "Nutrition"}
    ]
    
    db = SessionLocal()
    try:
        # Check if categories already exist
        existing_count = db.query(Category).count()
        if existing_count > 0:
            print("📂 Categories already exist, skipping initialization.")
            return
        
        # Add default categories
        for cat_data in default_categories:
            category = Category(**cat_data)
            db.add(category)
        
        db.commit()
        print(f"✅ Added {len(default_categories)} default categories!")
        
    except IntegrityError as e:
        db.rollback()
        print(f"⚠️  Categories already exist or integrity error: {e}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error initializing categories: {e}")
        raise
    finally:
        db.close()

# =========================
#  DATABASE UTILITIES
# =========================
def reset_db():
    """Reset database - drop all tables and recreate with categories"""
    print("🔄 Resetting database...")
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("🗑️  All tables dropped")
    
    # Recreate tables and initialize with default data
    Base.metadata.create_all(bind=engine)
    print("🏗️  All tables recreated")
    
    # Initialize with default categories
    init_categories()
    print("✅ Database reset complete!")

def init_categories():
    """Initialize only the categories (helper for reset_db)"""
    from models import Category
    
    default_categories = [
        {"name": "Strength"},
        {"name": "Learning"}, 
        {"name": "Relationship"},
        {"name": "Spirituality"},
        {"name": "Career"},
        {"name": "Sleep"},
        {"name": "Nutrition"}
    ]
    
    db = SessionLocal()
    try:
        # Add default categories
        for cat_data in default_categories:
            category = Category(**cat_data)
            db.add(category)
        
        db.commit()
        print(f"✅ Added {len(default_categories)} default categories!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding categories: {e}")
        raise
    finally:
        db.close()

def check_db_connection():
    """Check if database connection works"""
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"Database URL: {DATABASE_URL.replace(DATABASE_URL.split('@')[0].split(':')[-1], '****')}")  # Hide password in logs
        return False

# =========================
#  CALL INIT_DB WHEN RUN DIRECTLY
# =========================
if __name__ == "__main__":
    print("🚀 Initializing Seikatsu database...")
    if check_db_connection():
        init_db()
        print("🎯 Database ready for Seikatsu app!")
    else:
        print("❌ Database initialization failed due to connection issues")