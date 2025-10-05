"""
Tasks Service
Handles task completion logic, XP rewards, streaks, and task management.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, cast
import logging
from models import Task, User
from services.xp_manager import add_xp, XP_REWARDS

logger = logging.getLogger(__name__)


def get_utc_now() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


def complete_task(
    db: Session,
    user_id: int,
    task_id: int,
    category_id: Optional[int] = None
) -> Dict:
    """
    Mark a task as completed and award XP.
    
    Args:
        db: Database session
        user_id: User ID
        task_id: Task ID to complete
        category_id: Optional category to assign XP to (defaults to general category)
        
    Returns:
        Dictionary with task completion details and XP info
    """
    try:
        # Get the task
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()
        
        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id}")
        
        if task.is_completed:
            return {
                "success": False,
                "message": "Task already completed",
                "task_id": task_id
            }
        
        # Mark as completed
        task.is_completed = True
        task.completed_at = get_utc_now()  # type: ignore[assignment]
        
        # Award XP
        xp_reward = task.xp_reward or XP_REWARDS["task_completion"]
        
        # If no category specified, use a default (you should have a "General" category)
        if not category_id:
            category_id = 1  # Assuming 1 is your default/general category
        
        xp_result = add_xp(
            db=db,
            user_id=user_id,
            category_id=category_id,
            amount=xp_reward,
            reason=f"Completed task: {task.title}"
        )
        
        db.commit()
        db.refresh(task)
        
        logger.info(f"User {user_id} completed task {task_id} and earned {xp_reward} XP")
        
        return {
            "success": True,
            "message": "Task completed successfully!",
            "task_id": task_id,
            "task_title": task.title,
            "xp_earned": xp_reward,
            "xp_details": xp_result,
            "completed_at": task.completed_at
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error completing task {task_id} for user {user_id}: {str(e)}")
        raise


def uncomplete_task(db: Session, user_id: int, task_id: int) -> Dict:
    """
    Mark a task as incomplete (undo completion).
    Note: Does not deduct XP to avoid abuse.
    
    Args:
        db: Database session
        user_id: User ID
        task_id: Task ID to uncomplete
        
    Returns:
        Dictionary with task details
    """
    try:
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()
        
        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id}")
        
        if not task.is_completed:
            return {
                "success": False,
                "message": "Task is not completed",
                "task_id": task_id
            }
        
        task.is_completed = False
        task.completed_at = None  # type: ignore[assignment]
        
        db.commit()
        db.refresh(task)
        
        logger.info(f"User {user_id} uncompleted task {task_id}")
        
        return {
            "success": True,
            "message": "Task marked as incomplete",
            "task_id": task_id,
            "task_title": task.title
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error uncompleting task {task_id} for user {user_id}: {str(e)}")
        raise


def reset_daily_tasks(db: Session) -> Dict:
    """
    Auto-reset daily recurring tasks.
    This should be run as a scheduled job (e.g., at midnight).
    
    Note: Requires a 'is_recurring' or 'frequency' field in Task model.
    For now, this is a placeholder implementation.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with reset statistics
    """
    try:
        # This would require additional fields in the Task model:
        # - is_recurring: bool
        # - frequency: str (daily, weekly, monthly)
        # - last_reset: datetime
        
        # For now, we'll just provide the structure
        logger.info("Daily task reset triggered")
        
        # Example implementation (commented out until model is updated):
        """
        today = get_utc_now().date()
        
        # Find all daily recurring tasks that were completed yesterday
        tasks_to_reset = db.query(Task).filter(
            Task.is_recurring == True,
            Task.frequency == "daily",
            Task.is_completed == True,
            func.date(Task.completed_at) < today
        ).all()
        
        reset_count = 0
        for task in tasks_to_reset:
            task.is_completed = False
            task.completed_at = None  # type: ignore[assignment]
            task.last_reset = get_utc_now()  # type: ignore[assignment]
            reset_count += 1
        
        db.commit()
        """
        
        return {
            "success": True,
            "message": "Daily tasks reset (feature requires model update)",
            "tasks_reset": 0
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting daily tasks: {str(e)}")
        raise


def get_due_tasks(db: Session, user_id: int, days_ahead: int = 7) -> List[Task]:
    """
    Get upcoming tasks due within the specified number of days.
    
    Args:
        db: Database session
        user_id: User ID
        days_ahead: Number of days to look ahead (default: 7)
        
    Returns:
        List of Task objects
    """
    try:
        now = get_utc_now()
        end_date = now + timedelta(days=days_ahead)
        
        tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.is_completed == False,
            Task.due_date.isnot(None),
            Task.due_date >= now,  # type: ignore[operator]
            Task.due_date <= end_date  # type: ignore[operator]
        ).order_by(Task.due_date).all()
        
        logger.info(f"Found {len(tasks)} upcoming tasks for user {user_id}")
        
        return tasks
        
    except Exception as e:
        logger.error(f"Error getting due tasks for user {user_id}: {str(e)}")
        raise


def get_overdue_tasks(db: Session, user_id: int) -> List[Task]:
    """
    Get tasks that are past their due date and not completed.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of overdue Task objects
    """
    try:
        now = get_utc_now()
        
        tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.is_completed == False,
            Task.due_date.isnot(None),
            Task.due_date < now  # type: ignore[operator]
        ).order_by(Task.due_date).all()
        
        logger.info(f"Found {len(tasks)} overdue tasks for user {user_id}")
        
        return tasks
        
    except Exception as e:
        logger.error(f"Error getting overdue tasks for user {user_id}: {str(e)}")
        raise


def get_today_tasks(db: Session, user_id: int) -> Dict:
    """
    Get all tasks for today (completed and incomplete).
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dictionary with today's tasks categorized
    """
    try:
        today_start = get_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Tasks due today
        due_today = db.query(Task).filter(
            Task.user_id == user_id,
            Task.due_date >= today_start,  # type: ignore[operator]
            Task.due_date < today_end  # type: ignore[operator]
        ).all()
        
        # Tasks completed today
        completed_today = db.query(Task).filter(
            Task.user_id == user_id,
            Task.is_completed == True,
            Task.completed_at >= today_start,  # type: ignore[operator]
            Task.completed_at < today_end  # type: ignore[operator]
        ).all()
        
        incomplete = [t for t in due_today if not t.is_completed]
        complete = [t for t in due_today if t.is_completed]
        
        return {
            "date": today_start.date().isoformat(),
            "due_today": len(due_today),
            "completed_today": len(completed_today),
            "incomplete_tasks": incomplete,
            "completed_tasks": complete,
            "completion_rate": (len(complete) / len(due_today) * 100) if due_today else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting today's tasks for user {user_id}: {str(e)}")
        raise


def bulk_complete_tasks(
    db: Session,
    user_id: int,
    task_ids: List[int],
    category_id: Optional[int] = None
) -> Dict:
    """
    Complete multiple tasks at once.
    
    Args:
        db: Database session
        user_id: User ID
        task_ids: List of task IDs to complete
        category_id: Optional category for XP rewards
        
    Returns:
        Dictionary with completion results
    """
    try:
        results = {
            "completed": [],
            "already_completed": [],
            "not_found": [],
            "total_xp_earned": 0
        }
        
        for task_id in task_ids:
            try:
                result = complete_task(db, user_id, task_id, category_id)
                
                if result["success"]:
                    results["completed"].append({
                        "task_id": task_id,
                        "title": result["task_title"],
                        "xp_earned": result["xp_earned"]
                    })
                    results["total_xp_earned"] += result["xp_earned"]
                else:
                    results["already_completed"].append(task_id)
                    
            except ValueError:
                results["not_found"].append(task_id)
            except Exception as e:
                logger.error(f"Error completing task {task_id}: {str(e)}")
                results["not_found"].append(task_id)
        
        return {
            "success": True,
            "results": results,
            "message": f"Completed {len(results['completed'])} tasks, earned {results['total_xp_earned']} XP"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in bulk complete for user {user_id}: {str(e)}")
        raise


def get_task_statistics(db: Session, user_id: int, days: int = 30) -> Dict:
    """
    Get detailed task statistics for a user over a period.
    
    Args:
        db: Database session
        user_id: User ID
        days: Number of days to analyze (default: 30)
        
    Returns:
        Dictionary with task statistics
    """
    try:
        start_date = get_utc_now() - timedelta(days=days)
        
        # All tasks in period
        all_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.created_at >= start_date  # type: ignore[operator]
        ).all()
        
        # Completed tasks in period
        completed = [t for t in all_tasks if t.is_completed]
        
        # Overdue tasks
        now = get_utc_now()
        overdue = [
            t for t in all_tasks
            if not t.is_completed and t.due_date and t.due_date < now  # type: ignore[operator]
        ]
        
        # Calculate average completion time
        completion_times = []
        for task in completed:
            if task.completed_at is not None and task.created_at is not None:
                # Convert both to datetime for subtraction
                completed_dt = task.completed_at if isinstance(task.completed_at, datetime) else task.completed_at
                created_dt = task.created_at if isinstance(task.created_at, datetime) else task.created_at
                time_diff = (completed_dt - created_dt).total_seconds() / 3600  # type: ignore[operator]
                completion_times.append(time_diff)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        return {
            "period_days": days,
            "total_tasks": len(all_tasks),
            "completed_tasks": len(completed),
            "incomplete_tasks": len(all_tasks) - len(completed),
            "overdue_tasks": len(overdue),
            "completion_rate": (len(completed) / len(all_tasks) * 100) if all_tasks else 0,
            "average_completion_time_hours": round(avg_completion_time, 2),
            "total_xp_earned": sum(t.xp_reward for t in completed),
        }
        
    except Exception as e:
        logger.error(f"Error getting task statistics for user {user_id}: {str(e)}")
        raise