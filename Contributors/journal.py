"""
Journal Management Routes
Handles all journal entry CRUD operations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
from deps import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Journal)
def create_journal(
    journal: schemas.JournalCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Create a new journal entry"""
    try:
        return crud.create_journal(db, journal, user_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating journal: {str(e)}")

@router.get("/", response_model=List[schemas.Journal])
def read_journals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get all journal entries for the current user"""
    if limit > 100:
        limit = 100  # Prevent large requests
    return crud.get_journals(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{journal_id}", response_model=schemas.Journal)
def read_journal(
    journal_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get a specific journal entry by ID"""
    journal = crud.get_journal(db, journal_id=journal_id)
    if journal is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    # Check if journal belongs to current user
    if journal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return journal

@router.put("/{journal_id}", response_model=schemas.Journal)
def update_journal(
    journal_id: int,
    journal_update: schemas.JournalUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Update a journal entry"""
    # First check if journal exists and belongs to user
    journal = crud.get_journal(db, journal_id=journal_id)
    if journal is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    if journal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    updated_journal = crud.update_journal(db, journal_id=journal_id, journal_update=journal_update)
    return updated_journal

@router.delete("/{journal_id}")
def delete_journal(
    journal_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Delete a journal entry"""
    # First check if journal exists and belongs to user
    journal = crud.get_journal(db, journal_id=journal_id)
    if journal is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    if journal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = crud.delete_journal(db, journal_id=journal_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete journal entry")
    
    return {"message": "Journal entry deleted successfully"}

@router.get("/search/by-mood/{mood}", response_model=List[schemas.Journal])
def search_journals_by_mood(
    mood: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Search journal entries by mood"""
    try:
        journals = crud.get_journals_by_mood(db, user_id=current_user.id, mood=mood)
        return journals
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching journals: {str(e)}")

@router.get("/stats/mood-summary")
def get_mood_summary(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get mood statistics summary"""
    try:
        mood_stats = crud.get_mood_statistics(db, user_id=current_user.id)
        return mood_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting mood stats: {str(e)}")

@router.get("/recent/entries", response_model=List[schemas.Journal])
def get_recent_journals(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get recent journal entries"""
    if days > 365:
        days = 365  # Limit to 1 year
    if days < 1:
        days = 1
        
    try:
        journals = crud.get_recent_journals(db, user_id=current_user.id, days=days)
        return journals
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent journals: {str(e)}")