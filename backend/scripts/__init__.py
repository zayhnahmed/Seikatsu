# scripts/__init__.py

"""
Seikatsu Backend Utility Scripts

This package contains standalone scripts for database management,
maintenance, and administrative tasks.

Available Scripts:
- seed_data.py: Initialize database with default categories and test data
- recalculate_xp.py: Recalculate XP and levels for users
- reset_streaks.py: Display and manage user streak information
- cleanup.py: Remove old log files and temporary data

Usage:
    python -m scripts.seed_data
    python -m scripts.recalculate_xp
    python -m scripts.cleanup
"""

__version__ = "1.0.0"