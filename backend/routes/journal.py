"""
Journal Routes - Journal Entry Management
Handles CRUD operations for journal entries with XP rewards
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import get_db
from logger import logger

router = APIRouter(
    prefix="/journal",
    tags=["Journal"]
)


@router.post("/", response_model=schemas.Journal, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    journal: schemas.JournalCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Create a new journal entry and award XP to the user.
    
    - **title**: Journal entry title (required)
    - **content**: Journal entry content (required)
    - **mood**: Optional mood indicator (e.g., "happy", "sad", "neutral")
    - **user_id**: User ID (required)
    
    **XP Reward**: User receives 20 XP for creating a journal entry.
    """
    try:
        # Verify user exists
        user = crud.get_user(db, user_id)
        if not user:
            logger.warning(f"Journal creation failed: User {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        # Create journal entry
        new_journal = crud.create_journal(db, journal, user_id)
        
        # Award XP for journaling (20 XP per entry)
        XP_REWARD = 20
        updated_stats = crud.update_user_xp(db, user_id, XP_REWARD)
        
        logger.info(
            f"Journal entry created: {new_journal.id} for user {user_id}. "
            f"Awarded {XP_REWARD} XP. New level: {updated_stats.level}, "
            f"Total XP: {updated_stats.total_xp}"
        )
        
        return new_journal
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating journal entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create journal entry"
        )


@router.get("/user/{user_id}", response_model=List[schemas.Journal])
async def get_user_journals(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all journal entries for a specific user with pagination.
    
    - **user_id**: User ID
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    
    Returns entries sorted by creation date (newest first).
    """
    try:
        # Verify user exists
        user = crud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        journals = crud.get_journals(db, user_id, skip, limit)
        logger.info(f"Retrieved {len(journals)} journal entries for user {user_id}")
        
        return journals
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching journals for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch journal entries"
        )


@router.get("/{journal_id}", response_model=schemas.Journal)
async def get_journal_entry(
    journal_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific journal entry by ID.
    
    - **journal_id**: Journal entry ID
    """
    try:
        journal = crud.get_journal(db, journal_id)
        if not journal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Journal entry with id {journal_id} not found"
            )
        
        logger.info(f"Retrieved journal entry: {journal_id}")
        return journal
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching journal {journal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch journal entry"
        )


@router.put("/{journal_id}", response_model=schemas.Journal)
async def update_journal_entry(
    journal_id: int,
    journal_update: schemas.JournalUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing journal entry.
    
    - **journal_id**: Journal entry ID
    - **title**: Optional updated title
    - **content**: Optional updated content
    - **mood**: Optional updated mood
    
    **Note**: Only provided fields will be updated.
    """
    try:
        # Check if journal exists
        journal = crud.get_journal(db, journal_id)
        if not journal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Journal entry with id {journal_id} not found"
            )
        
        # Update journal
        updated_journal = crud.update_journal(db, journal_id, journal_update)
        
        logger.info(f"Journal entry updated: {journal_id}")
        return updated_journal
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating journal {journal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update journal entry"
        )


@router.delete("/{journal_id}", response_model=schemas.MessageResponse)
async def delete_journal_entry(
    journal_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a journal entry.
    
    - **journal_id**: Journal entry ID
    
    **Note**: This does NOT deduct XP that was awarded for creating the entry.
    """
    try:
        # Check if journal exists
        journal = crud.get_journal(db, journal_id)
        if not journal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Journal entry with id {journal_id} not found"
            )
        
        # Delete journal
        success = crud.delete_journal(db, journal_id)
        
        if success:
            logger.info(f"Journal entry deleted: {journal_id}")
            return schemas.MessageResponse(
                message="Journal entry deleted successfully",
                detail=f"Journal {journal_id} has been removed"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete journal entry"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting journal {journal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete journal entry"
        )


@router.get("/user/{user_id}/count")
async def get_journal_count(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the total count of journal entries for a user.
    
    Useful for analytics and progress tracking.
    """
    try:
        # Verify user exists
        user = crud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        journals = crud.get_journals(db, user_id)
        count = len(journals)
        
        logger.info(f"User {user_id} has {count} journal entries")
        
        return {
            "user_id": user_id,
            "total_journals": count,
            "message": f"User has written {count} journal entries"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error counting journals for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to count journal entries"
        )


@router.get("/user/{user_id}/recent")
async def get_recent_journals(
    user_id: int,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Get the most recent journal entries for a user.
    
    - **user_id**: User ID
    - **limit**: Number of recent entries to return (default: 5)
    
    Useful for dashboard displays and quick access.
    """
    try:
        # Verify user exists
        user = crud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        journals = crud.get_journals(db, user_id, skip=0, limit=limit)
        
        logger.info(f"Retrieved {len(journals)} recent journals for user {user_id}")
        
        return journals
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching recent journals for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recent journal entries"
        )


@router.get("/user/{user_id}/moods")
async def get_mood_distribution(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get mood distribution for a user's journal entries.
    
    Returns a breakdown of how many entries have each mood.
    Useful for mood tracking and analytics.
    """
    try:
        # Verify user exists
        user = crud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        journals = crud.get_journals(db, user_id)
        
        # Count moods
        mood_counts = {}
        for journal in journals:
            mood = journal.mood if journal.mood else "unspecified"
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        logger.info(f"Retrieved mood distribution for user {user_id}")
        
        return {
            "user_id": user_id,
            "total_entries": len(journals),
            "mood_distribution": mood_counts,
            "message": f"Mood distribution for {len(journals)} journal entries"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching mood distribution for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch mood distribution"
        )