"""
Services package for Seikatsu backend.
Contains business logic layer between routes and CRUD operations.
"""

from .xp_manager import (
    add_xp,
    deduct_xp,
    calculate_level,
    get_xp_for_level,
    calculate_level_progress,
    check_level_up,
)

from .insights import (
    calculate_streaks,
    generate_radar_data,
    get_mood_trend,
    summarize_weekly_progress,
    get_activity_stats,
    get_recent_activity,
)

from .tasks_service import (
    complete_task,
    reset_daily_tasks,
    get_due_tasks,
    get_overdue_tasks,
)

__all__ = [
    # XP Manager
    "add_xp",
    "deduct_xp",
    "calculate_level",
    "get_xp_for_level",
    "calculate_level_progress",
    "check_level_up",
    # Insights
    "calculate_streaks",
    "generate_radar_data",
    "get_mood_trend",
    "summarize_weekly_progress",
    "get_activity_stats",
    "get_recent_activity",
    # Tasks Service
    "complete_task",
    "reset_daily_tasks",
    "get_due_tasks",
    "get_overdue_tasks",
]