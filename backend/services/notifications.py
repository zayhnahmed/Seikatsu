"""
Notifications Service
Handles push notifications, reminders, and streak alerts.
Future integration with Firebase/Expo Push Notifications.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, time
from typing import Dict, List, Optional
import logging
from models import User, Journal, Task
from services.insights import calculate_streaks

logger = logging.getLogger(__name__)

# Notification templates
NOTIFICATION_TEMPLATES = {
    "daily_reminder": {
        "title": "Time to reflect! 📝",
        "body": "Take a moment to journal about your day.",
        "priority": "normal"
    },
    "streak_milestone": {
        "title": "Streak Milestone! 🔥",
        "body": "You've reached a {days}-day streak! Keep it going!",
        "priority": "high"
    },
    "streak_warning": {
        "title": "Don't break your streak! ⚠️",
        "body": "You haven't journaled today. Your {days}-day streak is at risk!",
        "priority": "high"
    },
    "streak_lost": {
        "title": "Streak Lost 💔",
        "body": "Your {days}-day streak ended. Start fresh today!",
        "priority": "normal"
    },
    "task_due_soon": {
        "title": "Task Due Soon ⏰",
        "body": "{task_title} is due in {hours} hours.",
        "priority": "high"
    },
    "task_overdue": {
        "title": "Overdue Task 🚨",
        "body": "{task_title} is overdue. Complete it to earn XP!",
        "priority": "high"
    },
    "level_up": {
        "title": "Level Up! 🎉",
        "body": "Congratulations! You've reached level {level}!",
        "priority": "high"
    },
    "weekly_summary": {
        "title": "Your Weekly Progress 📊",
        "body": "You've completed {tasks} tasks and wrote {journals} journal entries this week!",
        "priority": "normal"
    }
}


class NotificationService:
    """Service for managing notifications."""
    
    def __init__(self, push_service=None):
        """
        Initialize notification service.
        
        Args:
            push_service: External push notification service (Expo/Firebase)
        """
        self.push_service = push_service
    
    def send_notification(
        self,
        user_id: int,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        priority: str = "normal"
    ) -> Dict:
        """
        Send a push notification to a user.
        
        Args:
            user_id: User ID
            title: Notification title
            body: Notification body
            data: Additional data payload
            priority: Notification priority (normal/high)
            
        Returns:
            Dictionary with send status
        """
        try:
            # This is where you'd integrate with Expo Push or Firebase
            # For now, we'll just log it
            
            notification = {
                "user_id": user_id,
                "title": title,
                "body": body,
                "data": data or {},
                "priority": priority,
                "sent_at": datetime.utcnow().isoformat()
            }
            
            if self.push_service:
                # Example Expo Push integration:
                # response = self.push_service.publish({
                #     "to": user_push_token,
                #     "title": title,
                #     "body": body,
                #     "data": data,
                #     "priority": priority
                # })
                pass
            
            logger.info(f"Notification sent to user {user_id}: {title}")
            
            return {
                "success": True,
                "notification": notification
            }
            
        except Exception as e:
            logger.error(f"Error sending notification to user {user_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


def send_daily_reminder(db: Session, user_id: int, notification_service: NotificationService) -> Dict:
    """
    Send daily journal reminder to user.
    
    Args:
        db: Database session
        user_id: User ID
        notification_service: NotificationService instance
        
    Returns:
        Dictionary with send status
    """
    try:
        # Check if user already journaled today
        today = datetime.utcnow().date()
        journal_today = db.query(Journal).filter(
            Journal.user_id == user_id,
            func.date(Journal.created_at) == today
        ).first()
        
        if journal_today:
            logger.info(f"User {user_id} already journaled today, skipping reminder")
            return {"success": False, "reason": "Already journaled today"}
        
        template = NOTIFICATION_TEMPLATES["daily_reminder"]
        
        return notification_service.send_notification(
            user_id=user_id,
            title=template["title"],
            body=template["body"],
            priority=template["priority"]
        )
        
    except Exception as e:
        logger.error(f"Error sending daily reminder to user {user_id}: {str(e)}")
        raise


def notify_streak_milestone(
    db: Session,
    user_id: int,
    streak_days: int,
    notification_service: NotificationService
) -> Dict:
    """
    Send notification when user reaches a streak milestone.
    
    Args:
        db: Database session
        user_id: User ID
        streak_days: Number of days in streak
        notification_service: NotificationService instance
        
    Returns:
        Dictionary with send status
    """
    try:
        # Only notify on milestone days (7, 14, 30, 60, 100, etc.)
        milestones = [7, 14, 21, 30, 60, 90, 100, 200, 365]
        
        if streak_days not in milestones:
            return {"success": False, "reason": "Not a milestone day"}
        
        template = NOTIFICATION_TEMPLATES["streak_milestone"]
        
        return notification_service.send_notification(
            user_id=user_id,
            title=template["title"],
            body=template["body"].format(days=streak_days),
            data={"streak_days": streak_days, "type": "milestone"},
            priority=template["priority"]
        )
        
    except Exception as e:
        logger.error(f"Error notifying milestone for user {user_id}: {str(e)}")
        raise


def notify_streak_warning(
    db: Session,
    user_id: int,
    notification_service: NotificationService
) -> Dict:
    """
    Alert user if their streak is at risk (haven't journaled today).
    
    Args:
        db: Database session
        user_id: User ID
        notification_service: NotificationService instance
        
    Returns:
        Dictionary with send status
    """
    try:
        streaks = calculate_streaks(db, user_id)
        
        # Only send if user has an active streak
        if streaks.journal_streak == 0:
            return {"success": False, "reason": "No active streak"}
        
        # Check if user journaled today
        today = datetime.utcnow().date()
        journal_today = db.query(Journal).filter(
            Journal.user_id == user_id,
            func.date(Journal.created_at) == today
        ).first()
        
        if journal_today:
            return {"success": False, "reason": "Already journaled today"}
        
        template = NOTIFICATION_TEMPLATES["streak_warning"]
        
        return notification_service.send_notification(
            user_id=user_id,
            title=template["title"],
            body=template["body"].format(days=streaks.journal_streak),
            data={"streak_days": streaks.journal_streak, "type": "warning"},
            priority=template["priority"]
        )
        
    except Exception as e:
        logger.error(f"Error sending streak warning to user {user_id}: {str(e)}")
        raise


def notify_streak_lost(
    db: Session,
    user_id: int,
    lost_streak: int,
    notification_service: NotificationService
) -> Dict:
    """
    Notify user when they lose their streak.
    
    Args:
        db: Database session
        user_id: User ID
        lost_streak: Number of days in lost streak
        notification_service: NotificationService instance
        
    Returns:
        Dictionary with send status
    """
    try:
        # Only notify if streak was significant (3+ days)
        if lost_streak < 3:
            return {"success": False, "reason": "Streak too short to notify"}
        
        template = NOTIFICATION_TEMPLATES["streak_lost"]
        
        return notification_service.send_notification(
            user_id=user_id,
            title=template["title"],
            body=template["body"].format(days=lost_streak),
            data={"lost_streak": lost_streak, "type": "streak_lost"},
            priority=template["priority"]
        )
        
    except Exception as e:
        logger.error(f"Error notifying streak loss for user {user_id}: {str(e)}")
        raise


def notify_task_due_soon(
    db: Session,
    user_id: int,
    task_id: int,
    notification_service: NotificationService,
    hours_before: int = 24
) -> Dict:
    """
    Notify user about upcoming task deadline.
    
    Args:
        db: Database session
        user_id: User ID
        task_id: Task ID
        notification_service: NotificationService instance
        hours_before: Hours before due date to notify (default: 24)
        
    Returns:
        Dictionary with send status
    """
    try:
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id,
            Task.is_completed == False
        ).first()
        
        if not task or not task.due_date:
            return {"success": False, "reason": "Task not found or no due date"}
        
        template = NOTIFICATION_TEMPLATES["task_due_soon"]
        
        return notification_service.send_notification(
            user_id=user_id,
            title=template["title"],
            body=template["body"].format(task_title=task.title, hours=hours_before),
            data={"task_id": task_id, "type": "task_due_soon"},
            priority=template["priority"]
        )
        
    except Exception as e:
        logger.error(f"Error notifying task due for user {user_id}: {str(e)}")
        raise


def notify_task_overdue(
    db: Session,
    user_id: int,
    task_id: int,
    notification_service: NotificationService
) -> Dict:
    """
    Notify user about overdue task.
    
    Args:
        db: Database session
        user_id: User ID
        task_id: Task ID
        notification_service: NotificationService instance
        
    Returns:
        Dictionary with send status
    """
    try:
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id,
            Task.is_completed == False
        ).first()
        
        if not task:
            return {"success": False, "reason": "Task not found"}
        
        template = NOTIFICATION_TEMPLATES["task_overdue"]
        
        return notification_service.send_notification(
            user_id=user_id,
            title=template["title"],
            body=template["body"].format(task_title=task.title),
            data={"task_id": task_id, "type": "task_overdue"},
            priority=template["priority"]
        )
        
    except Exception as e:
        logger.error(f"Error notifying overdue task for user {user_id}: {str(e)}")
        raise


def notify_level_up(
    db: Session,
    user_id: int,
    new_level: int,
    notification_service: NotificationService
) -> Dict:
    """
    Celebrate user leveling up.
    
    Args:
        db: Database session
        user_id: User ID
        new_level: New level achieved
        notification_service: NotificationService instance
        
    Returns:
        Dictionary with send status
    """
    try:
        template = NOTIFICATION_TEMPLATES["level_up"]
        
        return notification_service.send_notification(
            user_id=user_id,
            title=template["title"],
            body=template["body"].format(level=new_level),
            data={"level": new_level, "type": "level_up"},
            priority=template["priority"]
        )
        
    except Exception as e:
        logger.error(f"Error notifying level up for user {user_id}: {str(e)}")
        raise


def send_weekly_summary(
    db: Session,
    user_id: int,
    notification_service: NotificationService
) -> Dict:
    """
    Send weekly progress summary notification.
    
    Args:
        db: Database session
        user_id: User ID
        notification_service: NotificationService instance
        
    Returns:
        Dictionary with send status
    """
    try:
        from services.insights import summarize_weekly_progress
        
        summary = summarize_weekly_progress(db, user_id)
        
        template = NOTIFICATION_TEMPLATES["weekly_summary"]
        
        return notification_service.send_notification(
            user_id=user_id,
            title=template["title"],
            body=template["body"].format(
                tasks=summary["tasks_completed"],
                journals=summary["journals_written"]
            ),
            data={"summary": summary, "type": "weekly_summary"},
            priority=template["priority"]
        )
        
    except Exception as e:
        logger.error(f"Error sending weekly summary to user {user_id}: {str(e)}")
        raise


def schedule_notifications(db: Session, notification_service: NotificationService):
    """
    Main scheduler function to check and send all scheduled notifications.
    This should be called by a background task scheduler (e.g., APScheduler, Celery).
    
    Args:
        db: Database session
        notification_service: NotificationService instance
    """
    try:
        logger.info("Running scheduled notification checks...")
        
        # Get all users
        users = db.query(User).all()
        
        for user in users:
            try:
                # Send daily reminder (should be scheduled for user's preferred time)
                send_daily_reminder(db, user.id, notification_service)
                
                # Check for streak warnings
                notify_streak_warning(db, user.id, notification_service)
                
                # Check for due tasks (24 hours before)
                from services.tasks_service import get_due_tasks
                due_soon = get_due_tasks(db, user.id, days_ahead=1)
                
                for task in due_soon:
                    notify_task_due_soon(
                        db, user.id, task.id,
                        notification_service, hours_before=24
                    )
                
                # Check for overdue tasks
                from services.tasks_service import get_overdue_tasks
                overdue = get_overdue_tasks(db, user.id)
                
                for task in overdue:
                    notify_task_overdue(db, user.id, task.id, notification_service)
                
            except Exception as user_error:
                logger.error(f"Error processing notifications for user {user.id}: {str(user_error)}")
                continue
        
        logger.info("Completed scheduled notification checks")
        
    except Exception as e:
        logger.error(f"Error in notification scheduler: {str(e)}")
        raise


# Background task setup example (using APScheduler)
def setup_notification_scheduler(db: Session, notification_service: NotificationService):
    """
    Setup background scheduler for notifications.
    Requires: pip install apscheduler
    
    Example usage in main.py:
    
    from apscheduler.schedulers.background import BackgroundScheduler
    from services.notifications import setup_notification_scheduler
    
    scheduler = BackgroundScheduler()
    setup_notification_scheduler(get_db(), NotificationService())
    scheduler.start()
    """
    try:
        try:
            from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
            from apscheduler.triggers.cron import CronTrigger  # type: ignore
        except ImportError:
            logger.warning(
                "APScheduler not installed. "
                "Install with: pip install apscheduler"
            )
            raise
        
        scheduler = BackgroundScheduler()
        
        # Daily reminders at 8 PM
        scheduler.add_job(
            func=lambda: schedule_notifications(db, notification_service),
            trigger=CronTrigger(hour=20, minute=0),
            id='daily_reminders',
            name='Send daily reminders',
            replace_existing=True
        )
        
        # Weekly summary on Sundays at 6 PM
        scheduler.add_job(
            func=lambda: [
                send_weekly_summary(db, user.id, notification_service)
                for user in db.query(User).all()
            ],
            trigger=CronTrigger(day_of_week='sun', hour=18, minute=0),
            id='weekly_summary',
            name='Send weekly summaries',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Notification scheduler started successfully")
        
        return scheduler
        
    except Exception as e:
        logger.error(f"Error setting up notification scheduler: {str(e)}")
        raise