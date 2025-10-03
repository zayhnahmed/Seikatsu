"""
Insights Routes
Provides analytics, trends, and AI-powered insights for user data
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import crud, schemas
from database import get_db
from logger import logger
from .auth import get_current_user_id

router = APIRouter()

# ===================== #
#  ANALYTICS ENDPOINTS
# ===================== #

@router.get("/dashboard", response_model=Dict[str, Any])
def get_dashboard_insights(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard insights
    
    Returns:
    - Activity statistics
    - Level progress
    - Recent activity summary
    - Task completion trends
    """
    try:
        # Get activity stats
        activity_stats = crud.get_user_activity_stats(db, user_id)
        
        # Get level progress
        level_progress = crud.get_level_progress(db, user_id)
        
        # Get recent activity (last 7 days)
        recent_activity = crud.get_recent_activity(db, user_id, days=7)
        
        # Get pending tasks count
        pending_tasks = crud.get_pending_tasks(db, user_id)
        
        return {
            "activity_stats": activity_stats,
            "level_progress": level_progress,
            "recent_journals_count": len(recent_activity.journals),
            "recent_completed_tasks_count": len(recent_activity.completed_tasks),
            "pending_tasks_count": len(pending_tasks),
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating dashboard insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate dashboard insights"
        )


@router.get("/streaks/{user_id}", response_model=Dict[str, Any])
def get_journaling_streaks(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Calculate daily journaling streaks
    
    Returns:
    - Current streak (consecutive days)
    - Longest streak ever
    - Total journaling days
    - Last journal date
    
    TODO: Implement streak calculation logic in services layer
    """
    try:
        # Verify access (user can only see their own streaks)
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other users' streaks"
            )
        
        journals = crud.get_journals(db, user_id)
        
        if not journals:
            return {
                "current_streak": 0,
                "longest_streak": 0,
                "total_days": 0,
                "last_journal_date": None
            }
        
        # TODO: Implement proper streak calculation
        # For now, return basic stats
        journal_dates = set([datetime.fromisoformat(str(j.created_at)).date() for j in journals if j.created_at])
        
        return {
            "current_streak": 0,  # TODO: Calculate
            "longest_streak": 0,  # TODO: Calculate
            "total_days": len(journal_dates),
            "last_journal_date": max(journal_dates).isoformat() if journal_dates else None,
            "note": "Full streak calculation coming soon"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating streaks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate journaling streaks"
        )


@router.get("/mood/{user_id}", response_model=Dict[str, Any])
def get_mood_trends(
    user_id: int,
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Analyze mood trends from journal entries
    
    Returns mood distribution and trends over specified period
    
    TODO: Integrate with AI sentiment analysis for deeper insights
    """
    try:
        # Verify access
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other users' mood data"
            )
        
        # Get recent journals
        recent_activity = crud.get_recent_activity(db, user_id, days=days)
        journals = recent_activity.journals
        
        # Count mood occurrences
        mood_counts = {}
        for journal in journals:
            if journal.mood:
                mood_counts[journal.mood] = mood_counts.get(journal.mood, 0) + 1
        
        # Calculate percentages
        total_with_mood = sum(mood_counts.values())
        mood_percentages = {
            mood: (count / total_with_mood * 100) if total_with_mood > 0 else 0
            for mood, count in mood_counts.items()
        }
        
        return {
            "period_days": days,
            "total_entries": len(journals),
            "entries_with_mood": total_with_mood,
            "mood_distribution": mood_counts,
            "mood_percentages": mood_percentages,
            "most_common_mood": max(mood_counts.items(), key=lambda x: x[1])[0] if mood_counts else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing mood trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze mood trends"
        )


@router.get("/radar/{user_id}", response_model=Dict[str, Any])
def get_category_balance_radar(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Generate category balance radar chart data
    
    Analyzes user's task completion across different life categories:
    - Physical (exercise, health)
    - Mental (learning, creativity)
    - Social (relationships, networking)
    - Work (career, productivity)
    - Rest (sleep, relaxation)
    
    TODO: Implement category tagging system for tasks
    """
    try:
        # Verify access
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other users' category data"
            )
        
        # Get completed tasks
        completed_tasks = crud.get_completed_tasks(db, user_id)
        
        # TODO: Implement category analysis when category system is ready
        # For now, return placeholder structure
        return {
            "categories": {
                "physical": 0,
                "mental": 0,
                "social": 0,
                "work": 0,
                "rest": 0
            },
            "total_tasks": len(completed_tasks),
            "note": "Category tagging system coming soon"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating radar data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate category balance data"
        )


@router.get("/weekly/{user_id}", response_model=Dict[str, Any])
def get_weekly_reflection(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered weekly reflection
    
    Analyzes the past week's activity and provides:
    - Key achievements
    - Patterns and trends
    - Personalized recommendations
    - Motivational insights
    
    TODO: Integrate with AI service (OpenAI/Claude) for natural language generation
    """
    try:
        # Verify access
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other users' reflections"
            )
        
        # Get weekly activity
        weekly_activity = crud.get_recent_activity(db, user_id, days=7)
        activity_stats = crud.get_user_activity_stats(db, user_id)
        
        # Get completed tasks this week
        completed_this_week = len(weekly_activity.completed_tasks)
        journals_this_week = len(weekly_activity.journals)
        
        # TODO: Replace with actual AI-generated reflection
        reflection = {
            "week_summary": f"You completed {completed_this_week} tasks and wrote {journals_this_week} journal entries this week.",
            "achievements": [
                f"Maintained a {activity_stats.completion_rate:.1f}% task completion rate",
                f"Currently at Level {activity_stats.current_level}",
            ],
            "insights": [
                "Keep up the consistent journaling habit!",
                "Consider setting more challenging tasks to level up faster."
            ],
            "recommendations": [
                "Try journaling at the same time each day to build a stronger habit",
                "Break larger tasks into smaller, manageable subtasks"
            ],
            "generated_at": datetime.utcnow().isoformat(),
            "note": "AI-powered reflections coming soon"
        }
        
        return reflection
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating weekly reflection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate weekly reflection"
        )


@router.get("/productivity/{user_id}", response_model=Dict[str, Any])
def get_productivity_metrics(
    user_id: int,
    days: int = Query(30, ge=7, le=365, description="Analysis period in days"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Calculate productivity metrics and trends
    
    Returns:
    - Tasks completed per day average
    - XP earned per day average
    - Most productive day of week
    - Completion rate trends
    """
    try:
        # Verify access
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other users' productivity data"
            )
        
        # Get activity for period
        activity = crud.get_recent_activity(db, user_id, days=days)
        completed_tasks = activity.completed_tasks
        
        # Calculate metrics
        tasks_per_day = len(completed_tasks) / days if days > 0 else 0
        total_xp = sum(task.xp_reward or 0 for task in completed_tasks)
        xp_per_day = total_xp / days if days > 0 else 0
        
        return {
            "period_days": days,
            "total_tasks_completed": len(completed_tasks),
            "tasks_per_day_avg": round(tasks_per_day, 2),
            "total_xp_earned": total_xp,
            "xp_per_day_avg": round(xp_per_day, 2),
            "most_productive_day": "Coming soon",  # TODO: Implement
            "trend": "stable"  # TODO: Calculate trend
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating productivity metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate productivity metrics"
        )