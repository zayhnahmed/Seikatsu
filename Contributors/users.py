"""
User Management Routes
Handles user profiles, settings, and user-related operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
from deps import get_db, get_current_user

router = APIRouter()

@router.get("/me", response_model=schemas.UserWithStats)
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get current user profile with stats"""
    user_stats = crud.get_user_stats(db, user_id=current_user.id)
    return schemas.UserWithStats(
        **current_user.model_dump(),
        user_stats=user_stats
    )

@router.put("/me", response_model=schemas.User)
def update_current_user(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        updated_user = crud.update_user(db, user_id=current_user.id, user_update=user_update)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@router.delete("/me")
def delete_current_user(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Delete current user account"""
    try:
        success = crud.delete_user(db, user_id=current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User account deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

# ---- USER STATS / XP / LEVEL ROUTES ---- #
@router.get("/stats", response_model=schemas.UserStats)
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get current user XP and level"""
    stats = crud.get_user_stats(db, user_id=current_user.id)
    if stats is None:
        # Create stats if they don't exist
        stats = crud.create_user_stats(db, user_id=current_user.id)
    return stats

@router.post("/xp", response_model=schemas.UserStats)
def update_user_xp(
    xp_update: schemas.XPUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Manually update user XP (for testing or special events)"""
    if xp_update.xp_gained == 0:
        raise HTTPException(status_code=400, detail="XP gained cannot be zero")
    
    updated_stats = crud.update_user_xp(db, user_id=current_user.id, xp_gained=xp_update.xp_gained)
    return updated_stats

@router.get("/level-progress", response_model=schemas.LevelProgress)
def get_level_progress(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get detailed level progress information"""
    return crud.get_level_progress(db, user_id=current_user.id)

@router.post("/reset-xp", response_model=schemas.UserStats)
def reset_user_xp(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Reset user XP and level (for testing)"""
    stats = crud.reset_user_xp(db, user_id=current_user.id)
    if stats is None:
        raise HTTPException(status_code=404, detail="User stats not found")
    return stats

# ---- TASK MANAGEMENT ROUTES ---- #
@router.post("/tasks", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Create a new task"""
    try:
        return crud.create_task(db, task, user_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

@router.get("/tasks", response_model=List[schemas.Task])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get all tasks for the current user"""
    if limit > 100:
        limit = 100  # Prevent large requests
    return crud.get_tasks(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get a specific task by ID"""
    task = crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if task belongs to current user
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return task

@router.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Update a task"""
    # Check ownership
    task = crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    updated_task = crud.update_task(db, task_id=task_id, task_update=task_update)
    return updated_task

@router.put("/tasks/{task_id}/complete", response_model=schemas.Task)
def mark_task_complete(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Mark a task as complete and award XP"""
    # Check ownership
    task = crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    completed_task = crud.mark_task_complete(db, task_id=task_id)
    
    # Award XP for completing task
    if completed_task and not task.is_completed:  # Only award XP if task wasn't already completed
        xp_gained = int(completed_task.xp_reward) if completed_task.xp_reward else 10
        crud.update_user_xp(db, user_id=current_user.id, xp_gained=xp_gained)
    
    return completed_task

@router.put("/tasks/{task_id}/incomplete", response_model=schemas.Task)
def mark_task_incomplete(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Mark a task as incomplete (undo completion)"""
    task = crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Subtract XP if task was previously completed
    if bool(task.is_completed):
        xp_reward = getattr(task, 'xp_reward', 10) or 10
        xp_lost = -int(xp_reward)  # Negative XP to subtract
        crud.update_user_xp(db, user_id=current_user.id, xp_gained=xp_lost)
    
    updated_task = crud.mark_task_incomplete(db, task_id=task_id)
    return updated_task

@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Delete a task"""
    task = crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = crud.delete_task(db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete task")
    
    return {"message": "Task deleted successfully"}

@router.get("/tasks/completed", response_model=List[schemas.Task])
def get_completed_tasks(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get all completed tasks for current user"""
    return crud.get_completed_tasks(db, user_id=current_user.id)

@router.get("/tasks/pending", response_model=List[schemas.Task])
def get_pending_tasks(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get all pending tasks for current user"""
    return crud.get_pending_tasks(db, user_id=current_user.id)

# ---- CATEGORY MANAGEMENT ---- #
@router.get("/categories", response_model=List[schemas.Category])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    return crud.get_categories(db)

@router.get("/categories/{category_id}", response_model=schemas.Category)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get category by ID"""
    category = crud.get_category(db, category_id=category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/categories", response_model=schemas.Category)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Create a new category (admin only in future)"""
    try:
        return crud.create_category(db, category=category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating category: {str(e)}")