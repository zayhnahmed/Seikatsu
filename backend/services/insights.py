"""
Insights Service
Generates analytics, streaks, mood trends, and activity summaries.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from collections import Counter
from models import Journal, Task, Level, UserStats, Category, User
from schemas import ActivityStats, RecentActivity, InsightsSummary, Streaks

logger = logging.getLogger(__name__)


def calculate_streaks(db: Session, user_id: int) -> Streaks:
    """
    Calculate journaling and task completion streaks for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Streaks schema with current streak counts
    """
    try:
        # Calculate journal streak
        journal_streak = _calculate_journal_streak(db, user_id)
        
        # Calculate task completion streak
        task_streak = _calculate_task_streak(db, user_id)
        
        # Generate motivational message
        if journal_streak >= 7 and task_streak >= 7:
            message = f"🔥 Amazing! {journal_streak} day journal streak and {task_streak} day task streak!"
        elif journal_streak >= 7:
            message = f"🔥 {journal_streak} day journal streak! Keep it up!"
        elif task_streak >= 7:
            message = f"🔥 {task_streak} day task completion streak! Keep going!"
        elif journal_streak > 0 or task_streak > 0:
            message = "Keep building your streaks! Consistency is key."
        else:
            message = "Start your streak today! Small steps lead to big changes."
        
        return Streaks(
            journal_streak=journal_streak,
            task_completion_streak=task_streak,
            message=message
        )
        
    except Exception as e:
        logger.error(f"Error calculating streaks for user {user_id}: {str(e)}")
        raise


def _calculate_journal_streak(db: Session, user_id: int) -> int:
    """Calculate consecutive days with at least one journal entry."""
    today = datetime.utcnow().date()
    streak = 0
    current_date = today
    
    while True:
        # Check if user journaled on current_date
        journal_count = db.query(Journal).filter(
            Journal.user_id == user_id,
            func.date(Journal.created_at) == current_date
        ).count()
        
        if journal_count > 0:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            # Streak broken
            break
        
        # Prevent infinite loop - cap at 365 days
        if streak >= 365:
            break
    
    return streak


def _calculate_task_streak(db: Session, user_id: int) -> int:
    """Calculate consecutive days with at least one completed task."""
    today = datetime.utcnow().date()
    streak = 0
    current_date = today
    
    while True:
        # Check if user completed tasks on current_date
        task_count = db.query(Task).filter(
            Task.user_id == user_id,
            Task.is_completed == True,
            func.date(Task.completed_at) == current_date
        ).count()
        
        if task_count > 0:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            # Streak broken
            break
        
        # Prevent infinite loop - cap at 365 days
        if streak >= 365:
            break
    
    return streak


def generate_radar_data(db: Session, user_id: int) -> Dict:
    """
    Generate radar chart data showing XP/level distribution across categories.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dictionary with category names and their corresponding XP/levels
    """
    try:
        # Get all category levels for user
        category_levels = db.query(Level, Category).join(
            Category, Level.category_id == Category.id
        ).filter(Level.user_id == user_id).all()
        
        radar_data = {
            "categories": [],
            "levels": [],
            "xp": [],
            "normalized_scores": []  # Normalized to 0-100 scale for radar visualization
        }
        
        if not category_levels:
            return radar_data
        
        # Find max level for normalization
        max_level = max([level.level for level, _ in category_levels]) if category_levels else 1
        
        for level, category in category_levels:
            radar_data["categories"].append(category.name)
            radar_data["levels"].append(level.level)
            radar_data["xp"].append(level.xp)
            # Normalize level to 0-100 scale
            normalized = (level.level / max(max_level, 10)) * 100
            radar_data["normalized_scores"].append(round(normalized, 2))
        
        return radar_data
        
    except Exception as e:
        logger.error(f"Error generating radar data for user {user_id}: {str(e)}")
        raise


def get_mood_trend(db: Session, user_id: int, days: int = 30) -> Dict:
    """
    Analyze mood trends from journal entries over specified period.
    
    Args:
        db: Database session
        user_id: User ID
        days: Number of days to analyze (default: 30)
        
    Returns:
        Dictionary with mood distribution and trend analysis
    """
    try:
        # Get journals from the last N days
        start_date = datetime.utcnow() - timedelta(days=days)
        
        journals = db.query(Journal).filter(
            Journal.user_id == user_id,
            Journal.created_at >= start_date,
            Journal.mood.isnot(None)
        ).order_by(Journal.created_at).all()
        
        if not journals:
            return {
                "period_days": days,
                "total_entries": 0,
                "mood_distribution": {},
                "most_common_mood": None,
                "trend": "No data available"
            }
        
        # Count mood occurrences
        moods = [j.mood for j in journals if j.mood]
        mood_counts = Counter(moods)
        
        # Calculate percentages
        total = len(moods)
        mood_distribution = {
            mood: {
                "count": count,
                "percentage": round((count / total) * 100, 2)
            }
            for mood, count in mood_counts.items()
        }
        
        most_common = mood_counts.most_common(1)[0] if mood_counts else (None, 0)
        
        # Simple trend analysis (comparing first half vs second half)
        mid_point = len(journals) // 2
        first_half_moods = [j.mood for j in journals[:mid_point] if j.mood]
        second_half_moods = [j.mood for j in journals[mid_point:] if j.mood]
        
        trend = _analyze_mood_trend(first_half_moods, second_half_moods)
        
        return {
            "period_days": days,
            "total_entries": len(journals),
            "mood_distribution": mood_distribution,
            "most_common_mood": most_common[0],
            "trend": trend,
            "recent_moods": [
                {"date": str(j.created_at), "mood": j.mood}
                for j in journals[-7:]  # Last 7 entries
            ]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing mood trend for user {user_id}: {str(e)}")
        raise


def _analyze_mood_trend(first_half: List[str], second_half: List[str]) -> str:
    """Analyze if mood is improving, declining, or stable."""
    positive_moods = {"happy", "great", "excited", "joyful", "content", "peaceful"}
    negative_moods = {"sad", "angry", "anxious", "stressed", "frustrated", "tired"}
    
    def mood_score(moods):
        positive = sum(1 for m in moods if m.lower() in positive_moods)
        negative = sum(1 for m in moods if m.lower() in negative_moods)
        return positive - negative
    
    if not first_half or not second_half:
        return "Not enough data to determine trend"
    
    first_score = mood_score(first_half) / len(first_half)
    second_score = mood_score(second_half) / len(second_half)
    
    diff = second_score - first_score
    
    if diff > 0.2:
        return "Improving - Your mood seems to be getting better! 📈"
    elif diff < -0.2:
        return "Declining - Consider self-care activities 💙"
    else:
        return "Stable - Maintaining consistent emotional patterns"


def summarize_weekly_progress(db: Session, user_id: int) -> Dict:
    """
    Summarize user's activity and progress for the past week.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dictionary with weekly summary statistics
    """
    try:
        week_start = datetime.utcnow() - timedelta(days=7)
        
        # Count activities
        journal_count = db.query(Journal).filter(
            Journal.user_id == user_id,
            Journal.created_at >= week_start
        ).count()
        
        tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.created_at >= week_start
        ).all()
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.is_completed)
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Get XP gained this week
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        current_xp = user_stats.total_xp if user_stats else 0
        
        # Get categories with most activity
        category_activity = db.query(
            Category.name,
            func.count(Journal.id).label("activity_count")
        ).join(
            Level, Level.category_id == Category.id
        ).outerjoin(
            Journal, Journal.user_id == Level.user_id
        ).filter(
            Level.user_id == user_id,
            Journal.created_at >= week_start
        ).group_by(Category.name).order_by(desc("activity_count")).limit(3).all()
        
        top_categories = [
            {"name": name, "activity_count": count}
            for name, count in category_activity
        ]
        
        # Generate summary message
        if journal_count >= 5 and completion_rate >= 70:
            message = "🌟 Outstanding week! You're crushing your goals!"
        elif journal_count >= 3 or completion_rate >= 50:
            message = "💪 Great progress this week! Keep it up!"
        elif journal_count > 0 or completed_tasks > 0:
            message = "Good start! Let's build on this momentum."
        else:
            message = "Start fresh this week! Every journey begins with a single step."
        
        return {
            "period": "Last 7 days",
            "journals_written": journal_count,
            "tasks_created": total_tasks,
            "tasks_completed": completed_tasks,
            "completion_rate": round(completion_rate, 2),
            "current_total_xp": current_xp,
            "top_categories": top_categories,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Error summarizing weekly progress for user {user_id}: {str(e)}")
        raise


def get_activity_stats(db: Session, user_id: int) -> ActivityStats:
    """
    Get overall activity statistics for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        ActivityStats schema with comprehensive statistics
    """
    try:
        # Count journals
        total_journals = db.query(Journal).filter(Journal.user_id == user_id).count()
        
        # Count tasks
        total_tasks = db.query(Task).filter(Task.user_id == user_id).count()
        completed_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.is_completed == True
        ).count()
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        
        # Get user stats
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        
        return ActivityStats(
            total_journals=total_journals,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            completion_rate=round(completion_rate, 2),
            current_level=user_stats.level if user_stats else 1,
            total_xp=user_stats.total_xp if user_stats else 0
        )
        
    except Exception as e:
        logger.error(f"Error getting activity stats for user {user_id}: {str(e)}")
        raise


def get_recent_activity(
    db: Session,
    user_id: int,
    days: int = 7,
    limit: int = 10
) -> RecentActivity:
    """
    Get recent journals and completed tasks.
    
    Args:
        db: Database session
        user_id: User ID
        days: Number of days to look back (default: 7)
        limit: Maximum items to return per type (default: 10)
        
    Returns:
        RecentActivity schema with recent journals and tasks
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get recent journals
        journals = db.query(Journal).filter(
            Journal.user_id == user_id,
            Journal.created_at >= start_date
        ).order_by(desc(Journal.created_at)).limit(limit).all()
        
        # Get recently completed tasks
        completed_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.is_completed == True,
            Task.completed_at >= start_date
        ).order_by(desc(Task.completed_at)).limit(limit).all()
        
        return RecentActivity(
            journals=list(journals),
            completed_tasks=list(completed_tasks),
            period_days=days
        )
        
    except Exception as e:
        logger.error(f"Error getting recent activity for user {user_id}: {str(e)}")
        raise


def get_insights_summary(db: Session, user_id: int) -> InsightsSummary:
    """
    Get a quick summary of user insights.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        InsightsSummary schema with key metrics
    """
    try:
        stats = get_activity_stats(db, user_id)
        streaks = calculate_streaks(db, user_id)
        
        # Generate personalized message
        if stats.total_journals >= 10 and stats.completion_rate >= 70:
            message = "You're doing amazing! Your consistency is paying off. 🌟"
        elif stats.total_journals >= 5 or stats.completion_rate >= 50:
            message = "Great progress! Keep building those healthy habits. 💪"
        elif stats.total_journals > 0 or stats.completed_tasks > 0:
            message = "Nice start! Small steps lead to big changes. 🌱"
        else:
            message = "Welcome to Seikatsu! Start your journey today. ✨"
        
        return InsightsSummary(
            total_journal_entries=stats.total_journals,
            total_tasks=stats.total_tasks,
            completed_tasks=stats.completed_tasks,
            completion_rate=stats.completion_rate,
            message=message
        )
        
    except Exception as e:
        logger.error(f"Error getting insights summary for user {user_id}: {str(e)}")
        raise