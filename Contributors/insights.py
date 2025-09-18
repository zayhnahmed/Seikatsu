"""
Analytics & Insights Routes
Handles charts, streaks, mood trends, and user analytics
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import crud
import schemas
from deps import get_db, get_current_user

router = APIRouter()

@router.get("/summary", response_model=schemas.ActivityStats)
def get_insights_summary(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get comprehensive analytics summary"""
    return crud.get_user_activity_stats(db, user_id=current_user.id)

@router.get("/recent", response_model=schemas.RecentActivity)
def get_recent_activity(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get recent user activity"""
    if days > 365:
        days = 365  # Limit to 1 year
    if days < 1:
        days = 1
    
    return crud.get_recent_activity(db, user_id=current_user.id, days=days)

@router.get("/streaks", response_model=schemas.Streaks)
def get_streaks(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get streak information"""
    try:
        journal_streak = crud.calculate_journal_streak(db, user_id=current_user.id)
        task_streak = crud.calculate_task_completion_streak(db, user_id=current_user.id)
        
        return schemas.Streaks(
            journal_streak=journal_streak,
            task_completion_streak=task_streak,
            message="Keep up the momentum!"
        )
    except Exception as e:
        # Return default values if calculation fails
        return schemas.Streaks(
            journal_streak=0,
            task_completion_streak=0,
            message="Streak tracking temporarily unavailable"
        )

@router.get("/mood-trends")
def get_mood_trends(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get mood trends over time"""
    if days > 365:
        days = 365
    if days < 7:
        days = 7
    
    try:
        mood_data = crud.get_mood_trends(db, user_id=current_user.id, days=days)
        return {
            "period_days": days,
            "mood_distribution": mood_data.get("distribution", {}),
            "daily_moods": mood_data.get("daily_moods", []),
            "average_mood_score": mood_data.get("average_score", 0),
            "total_entries": mood_data.get("total_entries", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating mood trends: {str(e)}")

@router.get("/productivity-chart")
def get_productivity_chart(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get productivity chart data (tasks completed over time)"""
    if days > 365:
        days = 365
    if days < 7:
        days = 7
    
    try:
        productivity_data = crud.get_productivity_chart_data(db, user_id=current_user.id, days=days)
        return {
            "period_days": days,
            "daily_completions": productivity_data.get("daily_completions", []),
            "total_tasks_completed": productivity_data.get("total_completed", 0),
            "average_daily_completions": productivity_data.get("daily_average", 0),
            "best_day": productivity_data.get("best_day", None),
            "completion_trend": productivity_data.get("trend", "stable")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating productivity chart: {str(e)}")

@router.get("/xp-progression")
def get_xp_progression(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get XP progression over time"""
    if days > 365:
        days = 365
    if days < 7:
        days = 7
    
    try:
        xp_data = crud.get_xp_progression_data(db, user_id=current_user.id, days=days)
        return {
            "period_days": days,
            "daily_xp_gained": xp_data.get("daily_xp", []),
            "total_xp_gained": xp_data.get("total_gained", 0),
            "average_daily_xp": xp_data.get("daily_average", 0),
            "level_ups": xp_data.get("level_ups", []),
            "current_level": xp_data.get("current_level", 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting XP progression: {str(e)}")

@router.get("/weekly-summary")
def get_weekly_summary(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get weekly activity summary"""
    try:
        summary = crud.get_weekly_summary(db, user_id=current_user.id)
        return {
            "week_start": summary.get("week_start"),
            "week_end": summary.get("week_end"),
            "journals_written": summary.get("journals_count", 0),
            "tasks_completed": summary.get("tasks_completed", 0),
            "xp_gained": summary.get("xp_gained", 0),
            "streak_days": summary.get("streak_days", 0),
            "top_mood": summary.get("dominant_mood", "Unknown"),
            "productivity_score": summary.get("productivity_score", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating weekly summary: {str(e)}")

@router.get("/monthly-insights")
def get_monthly_insights(
    month: int = None,
    year: int = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get detailed monthly insights"""
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year
    
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    if year < 2020 or year > datetime.now().year + 1:
        raise HTTPException(status_code=400, detail="Invalid year")
    
    try:
        insights = crud.get_monthly_insights(db, user_id=current_user.id, month=month, year=year)
        return {
            "month": month,
            "year": year,
            "total_journal_entries": insights.get("journal_count", 0),
            "total_tasks_completed": insights.get("tasks_completed", 0),
            "total_xp_gained": insights.get("xp_gained", 0),
            "average_mood": insights.get("average_mood", "Unknown"),
            "most_productive_day": insights.get("best_day", None),
            "completion_rate": insights.get("completion_rate", 0),
            "level_progress": insights.get("level_progress", {}),
            "goals_achieved": insights.get("goals_achieved", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating monthly insights: {str(e)}")

@router.get("/habit-tracker")
def get_habit_tracker(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Track habit consistency (journaling, task completion)"""
    if days > 365:
        days = 365
    if days < 7:
        days = 7
    
    try:
        habits = crud.get_habit_tracking_data(db, user_id=current_user.id, days=days)
        return {
            "period_days": days,
            "journaling_streak": habits.get("journal_streak", 0),
            "task_completion_streak": habits.get("task_streak", 0),
            "journaling_consistency": habits.get("journal_consistency", 0),
            "task_consistency": habits.get("task_consistency", 0),
            "daily_activity": habits.get("daily_activity", []),
            "recommendations": habits.get("recommendations", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting habit data: {str(e)}")

@router.get("/goals-progress")
def get_goals_progress(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get progress toward user goals (placeholder for future implementation)"""
    return {
        "message": "Goals tracking coming soon!",
        "current_level_goal": crud.get_level_progress(db, user_id=current_user.id),
        "suggested_goals": [
            "Write 7 journal entries this week",
            "Complete 10 tasks this week", 
            "Maintain a 3-day streak",
            "Reach level " + str(crud.get_user_stats(db, user_id=current_user.id).level + 1)
        ]
    }

@router.get("/export-data")
def export_user_data(
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Export user data (placeholder for future implementation)"""
    if format.lower() not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
    
    return {
        "message": f"Data export in {format.upper()} format coming soon!",
        "available_data": [
            "Journal entries",
            "Task history", 
            "XP progression",
            "Level achievements",
            "Mood tracking data"
        ],
        "note": "Export functionality will be added in future version"
    }