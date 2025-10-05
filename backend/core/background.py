"""
Background Tasks Manager
Handles non-blocking async operations for XP updates, insights recalculation,
and notification sending to keep API responses fast.
"""

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import logging

# Configure logging
logger = logging.getLogger("background")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# -------------------------
# Task Completion Background Processing
# -------------------------

def process_task_completion_background(
    background_tasks: BackgroundTasks,
    db: Session,
    user_id: int,
    task_id: int,
    category_id: Optional[int],
    xp_amount: int
):
    """
    Process all background operations after a task is completed.
    
    Operations:
    - Grant XP to user in specific category
    - Update overall user stats
    - Recalculate insights (streaks, radar data)
    - Check for level-ups and send notifications if needed
    
    Args:
        background_tasks: FastAPI BackgroundTasks instance
        db: Database session
        user_id: User ID
        task_id: Completed task ID
        category_id: Category ID for XP allocation (optional)
        xp_amount: Amount of XP to grant
    """
    # Import here to avoid circular dependencies
    from services.xp_manager import add_xp
    from services.insights import calculate_streaks
    from services.notifications import NotificationService, notify_level_up
    
    def _process_task_xp():
        try:
            logger.info(f"Processing task completion XP for user {user_id}, task {task_id}")
            
            # Add XP
            result = add_xp(
                db=db,
                user_id=user_id,
                category_id=category_id or 1,  # Default to general category if none specified
                amount=xp_amount,
                reason=f"Task completion: {task_id}"
            )
            
            # Check if user leveled up
            if result.get("overall_leveled_up"):
                new_level = result.get("overall_level")
                logger.info(f"User {user_id} leveled up to {new_level}!")
                
                # Send level-up notification
                notification_service = NotificationService()
                notify_level_up(db, user_id, int(new_level), notification_service)  # type: ignore
            
            logger.info(f"Task completion processing complete for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing task completion XP: {str(e)}", exc_info=True)
    
    # Add background task
    background_tasks.add_task(_process_task_xp)


# -------------------------
# Journal Entry Background Processing
# -------------------------

def process_journal_entry_background(
    background_tasks: BackgroundTasks,
    db: Session,
    user_id: int,
    journal_id: int,
    xp_amount: int = 20
):
    """
    Process all background operations after a journal entry is created.
    
    Operations:
    - Grant XP for journaling
    - Update streaks
    - Recalculate insights
    - Check for streak milestones and send notifications
    
    Args:
        background_tasks: FastAPI BackgroundTasks instance
        db: Database session
        user_id: User ID
        journal_id: Created journal entry ID
        xp_amount: XP to grant (default: 20)
    """
    from services.xp_manager import add_xp
    from services.insights import calculate_streaks
    from services.notifications import NotificationService, notify_streak_milestone
    
    def _process_journal_xp():
        try:
            logger.info(f"Processing journal entry XP for user {user_id}, journal {journal_id}")
            
            # Add XP (category_id=1 for general/journaling)
            result = add_xp(
                db=db,
                user_id=user_id,
                category_id=1,
                amount=xp_amount,
                reason=f"Journal entry: {journal_id}"
            )
            
            # Calculate streaks
            streaks = calculate_streaks(db, user_id)
            
            # Check for streak milestones
            if streaks.journal_streak > 0:
                milestones = [7, 14, 21, 30, 60, 90, 100, 200, 365]
                if streaks.journal_streak in milestones:
                    logger.info(f"User {user_id} reached streak milestone: {streaks.journal_streak} days!")
                    notification_service = NotificationService()
                    notify_streak_milestone(
                        db, user_id, streaks.journal_streak, notification_service
                    )
            
            # Check for level-up
            if result.get("overall_leveled_up"):
                from services.notifications import notify_level_up
                new_level = result.get("overall_level")
                if new_level is not None:
                    logger.info(f"User {user_id} leveled up to {new_level}!")
                    notification_service = NotificationService()
                    notify_level_up(db, user_id, int(new_level), notification_service)
            
            logger.info(f"Journal entry processing complete for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing journal entry XP: {str(e)}", exc_info=True)
    
    background_tasks.add_task(_process_journal_xp)


# -------------------------
# Insights Update Background Processing
# -------------------------

def update_user_insights_background(
    background_tasks: BackgroundTasks,
    db: Session,
    user_id: int
):
    """
    Recalculate and update all user insights in the background.
    
    Operations:
    - Recalculate streaks
    - Update radar chart data
    - Analyze mood trends
    - Generate activity summaries
    
    Args:
        background_tasks: FastAPI BackgroundTasks instance
        db: Database session
        user_id: User ID
    """
    from services.insights import (
        calculate_streaks,
        generate_radar_data,
        get_mood_trend,
        summarize_weekly_progress
    )
    
    def _update_insights():
        try:
            logger.info(f"Updating insights for user {user_id}")
            
            # Recalculate all insights
            calculate_streaks(db, user_id)
            generate_radar_data(db, user_id)
            get_mood_trend(db, user_id, days=30)
            summarize_weekly_progress(db, user_id)
            
            logger.info(f"Insights updated successfully for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating insights for user {user_id}: {str(e)}", exc_info=True)
    
    background_tasks.add_task(_update_insights)


# -------------------------
# Notification Sending Background Processing
# -------------------------

def send_notification_background(
    background_tasks: BackgroundTasks,
    db: Session,
    user_id: int,
    notification_type: str,
    **kwargs
):
    """
    Send notifications asynchronously without blocking API responses.
    
    Args:
        background_tasks: FastAPI BackgroundTasks instance
        db: Database session
        user_id: User ID
        notification_type: Type of notification (daily_reminder, streak_warning, etc.)
        **kwargs: Additional parameters for the notification
    """
    from services.notifications import (
        NotificationService,
        send_daily_reminder,
        notify_streak_warning,
        notify_task_due_soon,
        notify_task_overdue
    )
    
    def _send_notification():
        try:
            logger.info(f"Sending {notification_type} notification to user {user_id}")
            
            notification_service = NotificationService()
            
            if notification_type == "daily_reminder":
                send_daily_reminder(db, user_id, notification_service)
            
            elif notification_type == "streak_warning":
                notify_streak_warning(db, user_id, notification_service)
            
            elif notification_type == "task_due_soon":
                task_id = kwargs.get("task_id")
                hours_before = kwargs.get("hours_before", 24)
                if task_id is not None:
                    notify_task_due_soon(db, user_id, task_id, notification_service, hours_before)
                else:
                    logger.warning("task_due_soon notification missing task_id")
            
            elif notification_type == "task_overdue":
                task_id = kwargs.get("task_id")
                if task_id is not None:
                    notify_task_overdue(db, user_id, task_id, notification_service)
                else:
                    logger.warning("task_overdue notification missing task_id")
            
            else:
                logger.warning(f"Unknown notification type: {notification_type}")
            
            logger.info(f"Notification sent successfully to user {user_id}")
            
        except Exception as e:
            logger.error(
                f"Error sending {notification_type} notification to user {user_id}: {str(e)}",
                exc_info=True
            )
    
    background_tasks.add_task(_send_notification)


# -------------------------
# Weekly Summary Background Processing
# -------------------------

def send_weekly_summary_background(
    background_tasks: BackgroundTasks,
    db: Session,
    user_id: int
):
    """
    Generate and send weekly progress summary to user.
    
    Args:
        background_tasks: FastAPI BackgroundTasks instance
        db: Database session
        user_id: User ID
    """
    from services.insights import summarize_weekly_progress
    from services.notifications import NotificationService, send_weekly_summary
    
    def _send_summary():
        try:
            logger.info(f"Sending weekly summary to user {user_id}")
            
            notification_service = NotificationService()
            send_weekly_summary(db, user_id, notification_service)
            
            logger.info(f"Weekly summary sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending weekly summary to user {user_id}: {str(e)}", exc_info=True)
    
    background_tasks.add_task(_send_summary)


# -------------------------
# Batch User Processing
# -------------------------

def process_multiple_users_background(
    background_tasks: BackgroundTasks,
    db: Session,
    user_ids: list[int],
    operation: str
):
    """
    Process background operations for multiple users at once.
    Useful for scheduled tasks like daily reminders or weekly summaries.
    
    Args:
        background_tasks: FastAPI BackgroundTasks instance
        db: Database session
        user_ids: List of user IDs to process
        operation: Operation to perform (daily_reminder, weekly_summary, etc.)
    """
    def _batch_process():
        try:
            logger.info(f"Starting batch {operation} for {len(user_ids)} users")
            
            success_count = 0
            error_count = 0
            
            for user_id in user_ids:
                try:
                    if operation == "daily_reminder":
                        from services.notifications import NotificationService, send_daily_reminder
                        send_daily_reminder(db, user_id, NotificationService())
                    
                    elif operation == "weekly_summary":
                        from services.notifications import NotificationService, send_weekly_summary
                        send_weekly_summary(db, user_id, NotificationService())
                    
                    elif operation == "update_insights":
                        from services.insights import calculate_streaks
                        calculate_streaks(db, user_id)
                    
                    success_count += 1
                    
                except Exception as user_error:
                    logger.error(f"Error processing user {user_id}: {str(user_error)}")
                    error_count += 1
            
            logger.info(
                f"Batch {operation} complete: {success_count} succeeded, {error_count} failed"
            )
            
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}", exc_info=True)
    
    background_tasks.add_task(_batch_process)


# -------------------------
# Cleanup and Maintenance Tasks
# -------------------------

def cleanup_old_data_background(
    background_tasks: BackgroundTasks,
    db: Session,
    days_to_keep: int = 365
):
    """
    Clean up old data (optional maintenance task).
    Can be used to archive or delete very old entries.
    
    Args:
        background_tasks: FastAPI BackgroundTasks instance
        db: Database session
        days_to_keep: Number of days of data to keep
    """
    def _cleanup():
        try:
            from datetime import datetime, timedelta
            
            logger.info(f"Starting data cleanup (keeping last {days_to_keep} days)")
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Example: Archive old journals (implement based on your needs)
            # old_journals = db.query(models.Journal).filter(
            #     models.Journal.created_at < cutoff_date
            # ).all()
            
            logger.info("Data cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during data cleanup: {str(e)}", exc_info=True)
    
    background_tasks.add_task(_cleanup)


logger.info("✓ Background tasks module loaded")