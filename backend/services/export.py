"""
Export Service
Handles exporting user data to CSV, JSON, and PDF formats.
"""

from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import DateTime
from typing import Optional, Dict
import logging
import csv
import json
from io import StringIO, BytesIO
from models import Journal, Task, Level, UserStats, Category, User

logger = logging.getLogger(__name__)


def export_journals_to_csv(db: Session, user_id: int) -> str:
    """
    Export user's journals to CSV format.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        CSV content as string
    """
    try:
        journals = db.query(Journal).filter(
            Journal.user_id == user_id
        ).order_by(Journal.created_at).all()
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Title', 'Content', 'Mood', 'Created At'])
        
        # Write data
        for journal in journals:
            writer.writerow([
                journal.id,
                journal.title,
                journal.content,
                journal.mood or '',
                str(journal.created_at) if journal.created_at else ''
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        logger.info(f"Exported {len(journals)} journals to CSV for user {user_id}")
        
        return csv_content
        
    except Exception as e:
        logger.error(f"Error exporting journals to CSV for user {user_id}: {str(e)}")
        raise


def export_tasks_to_csv(db: Session, user_id: int) -> str:
    """
    Export user's tasks to CSV format.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        CSV content as string
    """
    try:
        tasks = db.query(Task).filter(
            Task.user_id == user_id
        ).order_by(Task.created_at).all()
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Title', 'Description', 'Is Completed',
            'Completed At', 'Due Date', 'XP Reward', 'Created At'
        ])
        
        # Write data
        for task in tasks:
            writer.writerow([
                task.id,
                task.title,
                task.description or '',
                'Yes' if task.is_completed else 'No',
                str(task.completed_at) if task.completed_at else '',
                str(task.due_date) if task.due_date else '',
                task.xp_reward,
                str(task.created_at) if task.created_at else ''
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        logger.info(f"Exported {len(tasks)} tasks to CSV for user {user_id}")
        
        return csv_content
        
    except Exception as e:
        logger.error(f"Error exporting tasks to CSV for user {user_id}: {str(e)}")
        raise


def export_user_data_to_json(db: Session, user_id: int) -> str:
    """
    Export all user data to JSON format.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        JSON content as string
    """
    try:
        # Get user info
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Get user stats
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        
        # Get journals
        journals = db.query(Journal).filter(Journal.user_id == user_id).all()
        
        # Get tasks
        tasks = db.query(Task).filter(Task.user_id == user_id).all()
        
        # Get levels
        levels = db.query(Level, Category).join(
            Category, Level.category_id == Category.id
        ).filter(Level.user_id == user_id).all()
        
        # Build export data
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": str(user.created_at) if user.created_at else '',
            },
            "stats": {
                "level": user_stats.level if user_stats else 1,
                "total_xp": user_stats.total_xp if user_stats else 0,
            } if user_stats else None,
            "journals": [
                {
                    "id": j.id,
                    "title": j.title,
                    "content": j.content,
                    "mood": j.mood,
                    "created_at": str(j.created_at) if j.created_at else ''
                }
                for j in journals
            ],
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "is_completed": t.is_completed,
                    "completed_at": str(t.completed_at) if t.completed_at else None,
                    "due_date": str(t.due_date) if t.due_date else None,
                    "xp_reward": t.xp_reward,
                    "created_at": str(t.created_at) if t.created_at else ''
                }
                for t in tasks
            ],
            "category_levels": [
                {
                    "category": category.name,
                    "level": level.level,
                    "xp": level.xp
                }
                for level, category in levels
            ]
        }
        
        json_content = json.dumps(export_data, indent=2)
        
        logger.info(f"Exported full user data to JSON for user {user_id}")
        
        return json_content
        
    except Exception as e:
        logger.error(f"Error exporting user data to JSON for user {user_id}: {str(e)}")
        raise


def export_insights_report(db: Session, user_id: int) -> Dict:
    """
    Generate a comprehensive insights report for export.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dictionary with insights data ready for export
    """
    try:
        from services.insights import (
            calculate_streaks,
            get_activity_stats,
            get_mood_trend,
            generate_radar_data,
            summarize_weekly_progress
        )
        
        # Gather all insights
        streaks = calculate_streaks(db, user_id)
        activity_stats = get_activity_stats(db, user_id)
        mood_trend = get_mood_trend(db, user_id, days=30)
        radar_data = generate_radar_data(db, user_id)
        weekly_progress = summarize_weekly_progress(db, user_id)
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "streaks": {
                "journal_streak": streaks.journal_streak,
                "task_completion_streak": streaks.task_completion_streak,
                "message": streaks.message
            },
            "activity_summary": {
                "total_journals": activity_stats.total_journals,
                "total_tasks": activity_stats.total_tasks,
                "completed_tasks": activity_stats.completed_tasks,
                "completion_rate": activity_stats.completion_rate,
                "current_level": activity_stats.current_level,
                "total_xp": activity_stats.total_xp
            },
            "mood_analysis": mood_trend,
            "category_distribution": radar_data,
            "weekly_progress": weekly_progress
        }
        
        logger.info(f"Generated insights report for user {user_id}")
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating insights report for user {user_id}: {str(e)}")
        raise


def export_insights_to_json(db: Session, user_id: int) -> str:
    """
    Export insights report as JSON string.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        JSON string with insights report
    """
    try:
        report = export_insights_report(db, user_id)
        return json.dumps(report, indent=2)
        
    except Exception as e:
        logger.error(f"Error exporting insights to JSON for user {user_id}: {str(e)}")
        raise


def create_backup(db: Session, user_id: int) -> Dict:
    """
    Create a complete backup of all user data.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dictionary with all export formats
    """
    try:
        backup = {
            "created_at": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "data": {
                "json": export_user_data_to_json(db, user_id),
                "journals_csv": export_journals_to_csv(db, user_id),
                "tasks_csv": export_tasks_to_csv(db, user_id),
                "insights": export_insights_report(db, user_id)
            }
        }
        
        logger.info(f"Created complete backup for user {user_id}")
        
        return backup
        
    except Exception as e:
        logger.error(f"Error creating backup for user {user_id}: {str(e)}")
        raise


# Note: PDF export would require additional libraries like reportlab or weasyprint
# Here's a placeholder structure:

def export_insights_to_pdf(db: Session, user_id: int, file_path: str) -> str:
    """
    Export insights to PDF format.
    
    Args:
        db: Database session
        user_id: User ID
        file_path: Path to save PDF file
        
    Returns:
        Path to created PDF file
    """
    # TODO: Implement PDF export using reportlab or weasyprint
    raise NotImplementedError("PDF export not yet implemented")