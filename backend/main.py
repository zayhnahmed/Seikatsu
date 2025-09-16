from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import models, schemas, crud
from database import SessionLocal, engine, check_db_connection, init_db

# Create tables on startup
models.Base.metadata.create_all(bind=engine)

# App initialization with metadata
app = FastAPI(
    title="Seikatsu Backend",
    version="1.0.0",
    description="A gamified personal development app with journaling, task management, and XP/leveling system"
) 

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # More specific origins for security
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ STARTUP EVENT ============ #
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting Seikatsu Backend...")
    if check_db_connection():
        init_db()
        print("✅ Database initialized successfully")
    else:
        print("❌ Database connection failed - app may not function properly")

# ============ ROUTES ============ #

# Base route
@app.get("/", response_model=dict)
def root():
    return {
        "message": "Welcome to Seikatsu Backend 🚀", 
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow()
    }

# ---- JOURNAL ENDPOINTS ---- #
@app.post("/journal/", response_model=schemas.Journal)
def create_journal(journal: schemas.JournalCreate, db: Session = Depends(get_db)):
    """Create a new journal entry"""
    try:
        return crud.create_journal(db, journal, user_id=1)  # temporary hardcode
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating journal: {str(e)}")

@app.get("/journal/", response_model=list[schemas.Journal])
def read_journals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all journal entries for a user"""
    if limit > 100:
        limit = 100  # Prevent large requests
    return crud.get_journals(db, user_id=1, skip=skip, limit=limit)

@app.get("/journal/{journal_id}", response_model=schemas.Journal)
def read_journal(journal_id: int, db: Session = Depends(get_db)):
    """Get a specific journal entry by ID"""
    journal = crud.get_journal(db, journal_id=journal_id)
    if journal is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return journal

@app.put("/journal/{journal_id}", response_model=schemas.Journal)
def update_journal(journal_id: int, journal_update: schemas.JournalUpdate, db: Session = Depends(get_db)):
    """Update a journal entry"""
    journal = crud.update_journal(db, journal_id=journal_id, journal_update=journal_update)
    if journal is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return journal

@app.delete("/journal/{journal_id}")
def delete_journal(journal_id: int, db: Session = Depends(get_db)):
    """Delete a journal entry"""
    success = crud.delete_journal(db, journal_id=journal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return {"message": "Journal entry deleted successfully"}

# ---- TASK ENDPOINTS ---- #
@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    try:
        return crud.create_task(db, task, user_id=1)  # temporary hardcode
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

@app.get("/tasks/", response_model=list[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all tasks for a user"""
    if limit > 100:
        limit = 100  # Prevent large requests
    return crud.get_tasks(db, user_id=1, skip=skip, limit=limit)

@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task by ID"""
    task = crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Update a task"""
    task = crud.update_task(db, task_id=task_id, task_update=task_update)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}/complete", response_model=schemas.Task)
def mark_task_complete(task_id: int, db: Session = Depends(get_db)):
    """Mark a task as complete and award XP"""
    task = crud.mark_task_complete(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Award XP for completing task
    xp_gained = int(task.xp_reward) if task.xp_reward else 10
    crud.update_user_xp(db, user_id=1, xp_gained=xp_gained)  # temporary hardcode
    
    return task

@app.put("/tasks/{task_id}/incomplete", response_model=schemas.Task)
def mark_task_incomplete(task_id: int, db: Session = Depends(get_db)):
    """Mark a task as incomplete (undo completion)"""
    task = crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Subtract XP if task was previously completed
    if bool(task.is_completed):
        xp_reward = getattr(task, 'xp_reward', 10) or 10
        xp_lost = -int(xp_reward)  # Negative XP to subtract
        crud.update_user_xp(db, user_id=1, xp_gained=xp_lost)
    
    updated_task = crud.mark_task_incomplete(db, task_id=task_id)
    return updated_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    success = crud.delete_task(db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

@app.get("/tasks/completed/", response_model=list[schemas.Task])
def get_completed_tasks(db: Session = Depends(get_db)):
    """Get all completed tasks for a user"""
    return crud.get_completed_tasks(db, user_id=1)

@app.get("/tasks/pending/", response_model=list[schemas.Task])
def get_pending_tasks(db: Session = Depends(get_db)):
    """Get all pending tasks for a user"""
    return crud.get_pending_tasks(db, user_id=1)

# ---- LEVELS/XP ENDPOINTS ---- #
@app.get("/user/stats", response_model=schemas.UserStats)
def get_user_stats(db: Session = Depends(get_db)):
    """Get current user XP and level"""
    stats = crud.get_user_stats(db, user_id=1)  # temporary hardcode
    if stats is None:
        # Create stats if they don't exist
        stats = crud.create_user_stats(db, user_id=1)
    return stats

@app.post("/user/xp", response_model=schemas.UserStats)
def update_user_xp(xp_update: schemas.XPUpdate, db: Session = Depends(get_db)):
    """Manually update user XP (for testing or special events)"""
    if xp_update.xp_gained == 0:
        raise HTTPException(status_code=400, detail="XP gained cannot be zero")
    
    updated_stats = crud.update_user_xp(db, user_id=1, xp_gained=xp_update.xp_gained)
    return updated_stats

@app.get("/user/level-progress", response_model=schemas.LevelProgress)
def get_level_progress(db: Session = Depends(get_db)):
    """Get detailed level progress information"""
    return crud.get_level_progress(db, user_id=1)  # temporary hardcode

@app.post("/user/reset-xp", response_model=schemas.UserStats)
def reset_user_xp(db: Session = Depends(get_db)):
    """Reset user XP and level (for testing)"""
    stats = crud.reset_user_xp(db, user_id=1)
    if stats is None:
        raise HTTPException(status_code=404, detail="User stats not found")
    return stats

# ---- ANALYTICS/INSIGHTS ENDPOINTS ---- #
@app.get("/insights/summary", response_model=schemas.ActivityStats)
def get_insights_summary(db: Session = Depends(get_db)):
    """Get analytics summary"""
    return crud.get_user_activity_stats(db, user_id=1)

@app.get("/insights/recent", response_model=schemas.RecentActivity)
def get_recent_activity(days: int = 7, db: Session = Depends(get_db)):
    """Get recent user activity"""
    if days > 365:
        days = 365  # Limit to 1 year
    if days < 1:
        days = 1
    
    return crud.get_recent_activity(db, user_id=1, days=days)

@app.get("/insights/streaks", response_model=schemas.Streaks)
def get_streaks(db: Session = Depends(get_db)):
    """Get streak information (placeholder)"""
    return schemas.Streaks(
        journal_streak=0,
        task_completion_streak=0,
        message="Streak tracking coming soon!"
    )

# ---- CATEGORY ENDPOINTS ---- #
@app.get("/categories/", response_model=list[schemas.Category])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    return crud.get_categories(db)

@app.get("/categories/{category_id}", response_model=schemas.Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get category by ID"""
    category = crud.get_category(db, category_id=category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.post("/categories/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    try:
        return crud.create_category(db, category=category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating category: {str(e)}")

# ---- USER ENDPOINTS (Placeholder for future auth implementation) ---- #
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    try:
        return crud.create_user(db, user=user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ---- AUTH ENDPOINTS (Placeholder for future JWT implementation) ---- #
@app.post("/auth/signup", response_model=schemas.MessageResponse)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """User signup (placeholder - will implement JWT later)"""
    try:
        user = crud.create_user(db, user=user_data)
        return schemas.MessageResponse(
            message="User created successfully",
            detail=f"Welcome {user.username}! JWT authentication coming soon."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@app.post("/auth/login", response_model=schemas.MessageResponse)
def login(username: str, password: str, db: Session = Depends(get_db)):
    """User login (placeholder - will implement JWT later)"""
    user = crud.get_user_by_username(db, username=username)
    if user and crud.verify_password(password, str(user.hashed_password)):
        return schemas.MessageResponse(
            message="Login successful",
            detail="JWT token generation coming soon!"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

# ---- HEALTH CHECK ENDPOINTS ---- #
@app.get("/health", response_model=schemas.HealthCheck)
def health_check():
    """Health check endpoint"""
    return schemas.HealthCheck(
        status="healthy",
        service="seikatsu-backend",
        timestamp=datetime.utcnow()
    )

@app.get("/version", response_model=schemas.VersionInfo)
def get_version():
    """Get API version"""
    return schemas.VersionInfo(
        version="1.0.0",
        app="Seikatsu Backend"
    )

# ---- ERROR HANDLERS ---- #
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Resource not found", 
        "detail": str(exc.detail) if hasattr(exc, 'detail') else "Not found",
        "path": str(request.url)
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal server error", 
        "detail": "Something went wrong on our end",
        "path": str(request.url)
    }

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return {
        "error": "Invalid input",
        "detail": str(exc),
        "path": str(request.url)
    }

# ---- APP CONFIGURATION ---- #
if __name__ == "__main__":
    import uvicorn
    print("🌟 Starting Seikatsu Backend Server...")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )