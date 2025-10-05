"""
Utility Functions
Reusable helper functions for dates, streaks, text processing, formatting, and validation.
Used across services, routes, and background tasks to avoid code duplication.
"""

from datetime import datetime, date, timedelta, timezone
from typing import Optional, Union, List
import re
import logging

logger = logging.getLogger("utils")


# -------------------------
# Date & Time Utilities
# -------------------------

def get_current_utc_datetime() -> datetime:
    """
    Get current UTC datetime with timezone awareness.
    
    Returns:
        Current UTC datetime
    """
    return datetime.now(timezone.utc)


def get_current_utc_date() -> date:
    """
    Get current UTC date.
    
    Returns:
        Current UTC date
    """
    return datetime.now(timezone.utc).date()


def days_between(date1: Union[date, datetime], date2: Union[date, datetime]) -> int:
    """
    Calculate absolute number of days between two dates.
    
    Args:
        date1: First date
        date2: Second date
        
    Returns:
        Absolute number of days between dates
    """
    if isinstance(date1, datetime):
        date1 = date1.date()
    if isinstance(date2, datetime):
        date2 = date2.date()
    
    return abs((date1 - date2).days)


def is_consecutive_day(last_date: Union[date, datetime], current_date: Optional[Union[date, datetime]] = None) -> bool:
    """
    Check if current_date is exactly one day after last_date.
    Used for streak calculations.
    
    Args:
        last_date: Last activity date
        current_date: Current date (defaults to today)
        
    Returns:
        True if dates are consecutive, False otherwise
    """
    if current_date is None:
        current_date = get_current_utc_date()
    
    if isinstance(last_date, datetime):
        last_date = last_date.date()
    if isinstance(current_date, datetime):
        current_date = current_date.date()
    
    return (current_date - last_date).days == 1


def is_same_day(date1: Union[date, datetime], date2: Union[date, datetime]) -> bool:
    """
    Check if two dates are on the same day.
    
    Args:
        date1: First date
        date2: Second date
        
    Returns:
        True if dates are the same day, False otherwise
    """
    if isinstance(date1, datetime):
        date1 = date1.date()
    if isinstance(date2, datetime):
        date2 = date2.date()
    
    return date1 == date2


def get_week_start_date(reference_date: Optional[Union[date, datetime]] = None) -> date:
    """
    Get the start of the week (Monday) for a given date.
    
    Args:
        reference_date: Reference date (defaults to today)
        
    Returns:
        Monday of that week
    """
    if reference_date is None:
        reference_date = get_current_utc_date()
    
    if isinstance(reference_date, datetime):
        reference_date = reference_date.date()
    
    # 0 = Monday, 6 = Sunday
    days_since_monday = reference_date.weekday()
    return reference_date - timedelta(days=days_since_monday)


def get_month_start_date(reference_date: Optional[Union[date, datetime]] = None) -> date:
    """
    Get the first day of the month for a given date.
    
    Args:
        reference_date: Reference date (defaults to today)
        
    Returns:
        First day of that month
    """
    if reference_date is None:
        reference_date = get_current_utc_date()
    
    if isinstance(reference_date, datetime):
        reference_date = reference_date.date()
    
    return reference_date.replace(day=1)


def format_datetime_for_display(dt: datetime) -> str:
    """
    Format datetime for human-readable display.
    
    Args:
        dt: Datetime to format
        
    Returns:
        Formatted string (e.g., "Jan 15, 2025 at 3:30 PM")
    """
    return dt.strftime("%b %d, %Y at %I:%M %p")


def format_date_for_display(d: date) -> str:
    """
    Format date for human-readable display.
    
    Args:
        d: Date to format
        
    Returns:
        Formatted string (e.g., "January 15, 2025")
    """
    return d.strftime("%B %d, %Y")


# -------------------------
# Streak Calculation Helpers
# -------------------------

def calculate_streak_status(
    last_activity_date: Union[date, datetime],
    current_date: Optional[Union[date, datetime]] = None
) -> dict:
    """
    Calculate streak status based on last activity.
    
    Args:
        last_activity_date: Date of last activity
        current_date: Current date (defaults to today)
        
    Returns:
        Dictionary with streak status:
        - continues: bool (streak continues)
        - broke: bool (streak was broken)
        - same_day: bool (activity already done today)
    """
    if current_date is None:
        current_date = get_current_utc_date()
    
    if isinstance(last_activity_date, datetime):
        last_activity_date = last_activity_date.date()
    if isinstance(current_date, datetime):
        current_date = current_date.date()
    
    days_diff = (current_date - last_activity_date).days
    
    return {
        "continues": days_diff == 1,  # Yesterday
        "same_day": days_diff == 0,   # Today
        "broke": days_diff > 1         # More than 1 day ago
    }


def get_streak_emoji(streak_days: int) -> str:
    """
    Get appropriate emoji for streak length.
    
    Args:
        streak_days: Number of consecutive days
        
    Returns:
        Emoji string
    """
    if streak_days >= 100:
        return "💯"
    elif streak_days >= 30:
        return "🔥"
    elif streak_days >= 7:
        return "⭐"
    elif streak_days >= 3:
        return "✨"
    else:
        return "🌱"


# -------------------------
# Text Processing & Normalization
# -------------------------

def normalize_text(text: str) -> str:
    """
    Normalize text by stripping whitespace and converting to lowercase.
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
    """
    return text.strip().lower()


def clean_whitespace(text: str) -> str:
    """
    Clean excessive whitespace from text.
    Converts multiple spaces/newlines to single space.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    return re.sub(r'\s+', ' ', text).strip()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.
    
    Args:
        text: Input text
        max_length: Maximum length (default: 100)
        suffix: Suffix to add if truncated (default: "...")
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].rstrip() + suffix


def extract_hashtags(text: str) -> List[str]:
    """
    Extract hashtags from text.
    Useful for categorizing journal entries or tasks.
    
    Args:
        text: Input text
        
    Returns:
        List of hashtags (without # symbol)
    """
    hashtag_pattern = r'#(\w+)'
    matches = re.findall(hashtag_pattern, text)
    return [tag.lower() for tag in matches]


def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Input text
        
    Returns:
        Word count
    """
    return len(text.split())


def sanitize_input(text: str) -> str:
    """
    Basic sanitization for user input.
    Removes potential harmful characters but preserves basic formatting.
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    # Remove null bytes and other control characters
    text = text.replace('\0', '')
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


# -------------------------
# XP & Level Formatting
# -------------------------

def format_xp(xp: int) -> str:
    """
    Format XP for display with abbreviated notation.
    
    Args:
        xp: Experience points
        
    Returns:
        Formatted XP string (e.g., "1.2k XP", "500 XP")
    """
    if xp >= 1_000_000:
        return f"{xp/1_000_000:.1f}M XP"
    elif xp >= 1_000:
        return f"{xp/1_000:.1f}k XP"
    else:
        return f"{xp} XP"


def format_level_display(level: int, xp: int) -> str:
    """
    Format level and XP for display.
    
    Args:
        level: User level
        xp: Total XP
        
    Returns:
        Formatted string (e.g., "Level 5 (1.2k XP)")
    """
    return f"Level {level} ({format_xp(xp)})"


def calculate_completion_percentage(current: int, total: int) -> float:
    """
    Calculate completion percentage with safety checks.
    
    Args:
        current: Current progress
        total: Total required
        
    Returns:
        Percentage (0-100), rounded to 2 decimal places
    """
    if total <= 0:
        return 0.0
    
    percentage = (current / total) * 100
    return round(min(percentage, 100.0), 2)


# -------------------------
# Category & ID Helpers
# -------------------------

def get_category_id_by_name(category_name: str, default_id: int = 1) -> int:
    """
    Get category ID by name (basic mapping).
    Can be extended to query database if needed.
    
    Args:
        category_name: Category name
        default_id: Default category ID if not found
        
    Returns:
        Category ID
    """
    # Basic static mapping - extend this based on your categories
    category_map = {
        "personal": 1,
        "work": 2,
        "health": 3,
        "learning": 4,
        "creative": 5,
        "social": 6
    }
    
    normalized_name = normalize_text(category_name)
    return category_map.get(normalized_name, default_id)


def generate_display_id(prefix: str, numeric_id: int, padding: int = 6) -> str:
    """
    Generate a display-friendly ID with prefix.
    
    Args:
        prefix: ID prefix (e.g., "TSK", "JRN")
        numeric_id: Numeric ID
        padding: Number of digits to pad (default: 6)
        
    Returns:
        Formatted ID (e.g., "TSK-000042")
    """
    return f"{prefix}-{str(numeric_id).zfill(padding)}"


# -------------------------
# Validation Helpers
# -------------------------

def is_valid_mood(mood: str) -> bool:
    """
    Validate if mood string is in allowed list.
    
    Args:
        mood: Mood string
        
    Returns:
        True if valid mood, False otherwise
    """
    valid_moods = {
        "happy", "sad", "anxious", "excited", "angry", "peaceful",
        "stressed", "content", "frustrated", "grateful", "tired",
        "energetic", "calm", "worried", "joyful", "neutral"
    }
    
    return normalize_text(mood) in valid_moods


def is_valid_xp_amount(xp: int, min_xp: int = 0, max_xp: int = 10000) -> bool:
    """
    Validate XP amount is within reasonable bounds.
    
    Args:
        xp: XP amount
        min_xp: Minimum allowed XP (default: 0)
        max_xp: Maximum allowed XP (default: 10000)
        
    Returns:
        True if valid, False otherwise
    """
    return min_xp <= xp <= max_xp


def validate_pagination(skip: int, limit: int, max_limit: int = 100) -> tuple[int, int]:
    """
    Validate and normalize pagination parameters.
    
    Args:
        skip: Number of items to skip
        limit: Number of items to return
        max_limit: Maximum allowed limit (default: 100)
        
    Returns:
        Tuple of (validated_skip, validated_limit)
    """
    skip = max(0, skip)
    limit = max(1, min(limit, max_limit))
    return skip, limit


# -------------------------
# Data Transformation Helpers
# -------------------------

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero (default: 0.0)
        
    Returns:
        Division result or default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def clamp(value: Union[int, float], min_value: Union[int, float], max_value: Union[int, float]) -> Union[int, float]:
    """
    Clamp a value between minimum and maximum bounds.
    
    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_value, min(value, max_value))


def percentage_to_color(percentage: float) -> str:
    """
    Convert percentage to color indicator for UI.
    
    Args:
        percentage: Percentage (0-100)
        
    Returns:
        Color string (green/yellow/red)
    """
    if percentage >= 70:
        return "green"
    elif percentage >= 40:
        return "yellow"
    else:
        return "red"


# -------------------------
# Logging Helpers
# -------------------------

def log_operation(operation: str, entity: str, success: bool, **kwargs):
    """
    Standardized logging for operations.
    
    Args:
        operation: Operation type (CREATE, UPDATE, DELETE, etc.)
        entity: Entity type (User, Task, Journal, etc.)
        success: Whether operation succeeded
        **kwargs: Additional context to log
    """
    status = "SUCCESS" if success else "FAILED"
    context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    
    if success:
        logger.info(f"{operation} {entity} {status} | {context}")
    else:
        logger.error(f"{operation} {entity} {status} | {context}")


logger.info("✓ Utility functions module loaded")