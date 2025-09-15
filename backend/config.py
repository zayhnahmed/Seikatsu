from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from typing import List

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Centralized configuration for Seikatsu Backend
    Loads settings from environment variables (.env file)
    """
    
    # Database Configuration
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "Ahmed@5977")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5452")
    DB_NAME: str = os.getenv("DB_NAME", "postgres")
    
    # Alternative: Direct database URL (takes precedence if set)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Application Settings
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    
    @property
    def database_url(self) -> str:
        """
        Build database URL with proper password encoding
        Uses DATABASE_URL if provided, otherwise builds from individual components
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        encoded_password = quote_plus(self.DB_PASSWORD)
        return f"postgresql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.APP_ENV.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.APP_ENV.lower() == "production"
    
    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive = True,
    )

# Create settings instance
settings = Settings()

# Default categories for database initialization
DEFAULT_CATEGORIES = [
    {"name": "Strength"},
    {"name": "Learning"}, 
    {"name": "Relationship"},
    {"name": "Spirituality"},
    {"name": "Career"},
    {"name": "Sleep"},
    {"name": "Nutrition"}
]

# Helper function to validate configuration
def validate_config():
    """Validate critical configuration settings"""
    if settings.is_production and settings.SECRET_KEY == "your-secret-key-here-change-in-production":
        raise ValueError("❌ SECRET_KEY must be changed in production!")
    
    print(f"✅ Config loaded - Environment: {settings.APP_ENV}")
    print(f"✅ Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    print(f"✅ CORS Origins: {settings.ALLOWED_ORIGINS}")
    return True