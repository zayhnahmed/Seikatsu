"""
Task Routes
Handles task CRUD operations and task completion/tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import crud, schemas
from database import get_db
from logger import logger
from .auth import get_current_user_id

router = APIRouter()

# ===================== #
#  TASK ENDPOINTS
# ===================== #

@router.post("/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task: schemas.TaskCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new task
    
    - **title**: Task title/name (required)
    - **description**: Detailed task description (optional)
    - **xp_reward**: XP reward for completion (default: 10)
    - **due_date**: Optional deadline for the task
    
    Task starts in incomplete status
    """
    try:
        # Verify user exists
        user = crud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db_task = crud.create_task(db, task, user_id)
        return db_task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task"
        )


@router.get("/", response_model=List[schemas.Task])
def get_user_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum records to return"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all tasks for the authenticated user
    
    Returns all tasks (both completed and pending) sorted by creation date
    Use filter endpoints for completed/pending only
    """
    try:
        tasks = crud.get_tasks(db, user_id, skip=skip, limit=limit)
        return tasks
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tasks"
        )


@router.get("/completed", response_model=List[schemas.Task])
def get_completed_tasks(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all completed tasks for the authenticated user
    """
    try:
        tasks = crud.get_completed_tasks(db, user_id)
        return tasks
    except Exception as e:
        logger.error(f"Error fetching completed tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve completed tasks"
        )


@router.get("/pending", response_model=List[schemas.Task])
def get_pending_tasks(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all pending (incomplete) tasks for the authenticated user
    """
    try:
        tasks = crud.get_pending_tasks(db, user_id)
        return tasks
    except Exception as e:
        logger.error(f"Error fetching pending tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pending tasks"
        )


@router.get("/{task_id}", response_model=schemas.Task)
def get_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific task by ID
    
    Only accessible by the task owner
    """
    try:
        task = crud.get_task(db, task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Verify ownership
        if task.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this task"
            )
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task"
        )


@router.put("/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update an existing task
    
    Can update title, description, xp_reward, and due_date
    Does not change completion status (use complete/incomplete endpoints)
    """
    try:
        task = crud.get_task(db, task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Verify ownership
        if task.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this task"
            )
        
        updated_task = crud.update_task(db, task_id, task_update)
        return updated_task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )


@router.post("/{task_id}/complete", response_model=schemas.Task)
def complete_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Mark a task as completed
    
    Awards XP reward to the user
    Sets completion timestamp
    """
    try:
        task = crud.get_task(db, task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Verify ownership
        if task.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to complete this task"
            )
        
        # Check if already completed
        if task.is_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task already completed"
            )
        
        # Mark as complete
        completed_task = crud.mark_task_complete(db, task_id)
        
        # Award XP
        crud.update_user_xp(db, user_id, task.xp_reward)
        logger.info(f"User {user_id} gained {task.xp_reward} XP for completing task {task_id}")
        
        return completed_task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete task"
        )


@router.post("/{task_id}/incomplete", response_model=schemas.Task)
def mark_task_incomplete(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Mark a task as incomplete (undo completion)
    
    Does NOT deduct XP (XP is permanent once earned)
    Clears completion timestamp
    """
    try:
        task = crud.get_task(db, task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Verify ownership
        if task.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this task"
            )
        
        # Check if already incomplete
        if not task.is_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task is already incomplete"
            )
        
        # Mark as incomplete
        incomplete_task = crud.mark_task_incomplete(db, task_id)
        logger.info(f"Task {task_id} marked as incomplete (XP not deducted)")
        
        return incomplete_task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking task {task_id} incomplete: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark task as incomplete"
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a task
    
    Permanent action - cannot be undone
    XP already earned is not deducted
    """
    try:
        task = crud.get_task(db, task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Verify ownership
        if task.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this task"
            )
        
        success = crud.delete_task(db, task_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )