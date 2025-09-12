from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from passlib.context import CryptContext
import models, schemas

# ===================== #
#  PASSWORD HASHING SETUP
# ===================== #
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

# ===================== #
#  USER OPERATIONS
# ===================== #

def create_user(db: Session, user: schemas.UserCreate):
    """Create a new user with hashed password"""
    # Check if user already exists
    if get_user_by_username(db, user.username):
        raise ValueError("Username already exists")
    if get_user_by_email(db, user.email):
        raise ValueError("Email already exists")
    
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),  # FIXED: Hash password
        created_at=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create initial user stats
    create_user_stats(db, db_user.id)
    
    return db_user

def get_user(db: Session, user_id: int):
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    """Get user by username"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()

# ===================== #
#  JOURNAL OPERATIONS
# ===================== #

def create_journal(db: Session, journal: schemas.JournalCreate, user_id: int):
    """Create a new journal entry"""
    db_journal = models.Journal(
        title=journal.title,
        content=journal.content,
        mood=journal.mood,  # Include mood
        user_id=user_id,
        created_at=datetime.utcnow()
    )
    db.add(db_journal)
    db.commit()
    db.refresh(db_journal)
    return db_journal

def get_journals(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all journal entries for a user with pagination"""
    return db.query(models.Journal)\
             .filter(models.Journal.user_id == user_id)\
             .order_by(models.Journal.created_at.desc())\
             .offset(skip)\
             .limit(limit)\
             .all()

def get_journal(db: Session, journal_id: int):
    """Get a specific journal entry by ID"""
    return db.query(models.Journal)\
             .filter(models.Journal.id == journal_id)\
             .first()

def update_journal(db: Session, journal_id: int, journal_update: schemas.JournalUpdate):
    """Update an existing journal entry"""
    db_journal = get_journal(db, journal_id)
    if db_journal:
        # Only update fields that are provided
        if journal_update.title is not None:
            db_journal.title = journal_update.title
        if journal_update.content is not None:
            db_journal.content = journal_update.content
        if journal_update.mood is not None:
            db_journal.mood = journal_update.mood
        
        db.commit()
        db.refresh(db_journal)
    return db_journal

def delete_journal(db: Session, journal_id: int):
    """Delete a journal entry"""
    db_journal = get_journal(db, journal_id)
    if db_journal:
        db.delete(db_journal)
        db.commit()
        return True
    return False

# ===================== #
#  TASK OPERATIONS
# ===================== #

def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    """Create a new task"""
    db_task = models.Task(
        title=task.title,
        description=task.description,
        xp_reward=task.xp_reward or 10,
        due_date=task.due_date,
        user_id=user_id,
        is_completed=False,
        created_at=datetime.utcnow()
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all tasks for a user with pagination"""
    return db.query(models.Task)\
             .filter(models.Task.user_id == user_id)\
             .order_by(models.Task.created_at.desc())\
             .offset(skip)\
             .limit(limit)\
             .all()

def get_task(db: Session, task_id: int):
    """Get a specific task by ID"""
    return db.query(models.Task)\
             .filter(models.Task.id == task_id)\
             .first()

def mark_task_complete(db: Session, task_id: int):
    """Mark a task as completed"""
    db_task = get_task(db, task_id)
    if db_task and not db_task.is_completed:
        db_task.is_completed = True
        db_task.completed_at = datetime.utcnow()  # FIXED: Set completion timestamp
        db.commit()
        db.refresh(db_task)
    return db_task

def mark_task_incomplete(db: Session, task_id: int):
    """Mark a task as incomplete (undo completion)"""
    db_task = get_task(db, task_id)
    if db_task and db_task.is_completed:
        db_task.is_completed = False
        db_task.completed_at = None  # FIXED: Clear completion timestamp
        db.commit()
        db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    """Update an existing task"""
    db_task = get_task(db, task_id)
    if db_task:
        # Only update fields that are provided
        if task_update.title is not None:
            db_task.title = task_update.title
        if task_update.description is not None:
            db_task.description = task_update.description
        if task_update.xp_reward is not None:
            db_task.xp_reward = task_update.xp_reward
        if task_update.due_date is not None:
            db_task.due_date = task_update.due_date
            
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    """Delete a task"""
    db_task = get_task(db, task_id)
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

def get_completed_tasks(db: Session, user_id: int):
    """Get all completed tasks for a user"""
    return db.query(models.Task)\
             .filter(models.Task.user_id == user_id, models.Task.is_completed == True)\
             .all()

def get_pending_tasks(db: Session, user_id: int):
    """Get all pending (incomplete) tasks for a user"""
    return db.query(models.Task)\
             .filter(models.Task.user_id == user_id, models.Task.is_completed == False)\
             .all()

# ===================== #
#  USER STATS / XP / LEVEL OPERATIONS
# ===================== #

def get_user_stats(db: Session, user_id: int):
    """Get user stats (XP and level information)"""
    return db.query(models.UserStats)\
             .filter(models.UserStats.user_id == user_id)\
             .first()

def create_user_stats(db: Session, user_id: int):
    """Create initial user stats (level 1, 0 XP)"""
    db_stats = models.UserStats(
        user_id=user_id,
        level=1,
        total_xp=0
    )
    db.add(db_stats)
    db.commit()
    db.refresh(db_stats)
    return db_stats

def calculate_level_from_xp(total_xp: int) -> int:
    """Calculate user level based on total XP
    Formula: Each level requires level * 100 XP
    Level 1: 0-99 XP, Level 2: 100-299 XP, Level 3: 300-599 XP, etc.
    """
    if total_xp < 100:
        return 1
    
    level = 1
    cumulative_xp = 0
    
    while cumulative_xp <= total_xp:
        level += 1
        cumulative_xp += (level - 1) * 100
    
    return level - 1

def get_level_thresholds(level: int) -> tuple[int, int]:
    """Get XP thresholds for current and next level"""
    current_level_threshold = sum((i - 1) * 100 for i in range(2, level + 1))
    next_level_threshold = current_level_threshold + level * 100
    return current_level_threshold, next_level_threshold

def update_user_xp(db: Session, user_id: int, xp_gained: int):
    """Update user XP and recalculate level"""
    db_stats = get_user_stats(db, user_id)
    
    # Create stats if they don't exist
    if not db_stats:
        db_stats = create_user_stats(db, user_id)
    
    # Update XP
    db_stats.total_xp += xp_gained
    
    # Recalculate level
    new_level = calculate_level_from_xp(db_stats.total_xp)
    old_level = db_stats.level
    db_stats.level = new_level
    
    db.commit()
    db.refresh(db_stats)
    
    # You could add level-up rewards/notifications here
    if new_level > old_level:
        print(f"🎉 User {user_id} leveled up! {old_level} → {new_level}")
    
    return db_stats

def get_level_progress(db: Session, user_id: int) -> schemas.LevelProgress:
    """Get detailed level progress information"""
    stats = get_user_stats(db, user_id)
    if not stats:
        # Create stats if they don't exist
        stats = create_user_stats(db, user_id)
    
    # Calculate XP thresholds
    current_level_threshold, next_level_threshold = get_level_thresholds(stats.level)
    
    progress_in_current_level = stats.total_xp - current_level_threshold
    xp_needed_for_next = next_level_threshold - stats.total_xp
    
    # Calculate progress percentage within current level
    level_xp_requirement = next_level_threshold - current_level_threshold
    progress_percentage = (progress_in_current_level / level_xp_requirement) * 100 if level_xp_requirement > 0 else 0
    
    return schemas.LevelProgress(
        current_level=stats.level,
        total_xp=stats.total_xp,
        progress_in_current_level=progress_in_current_level,
        xp_needed_for_next_level=xp_needed_for_next,
        progress_percentage=progress_percentage,
        current_level_threshold=current_level_threshold,
        next_level_threshold=next_level_threshold
    )

def reset_user_xp(db: Session, user_id: int):
    """Reset user XP and level (for testing or special events)"""
    db_stats = get_user_stats(db, user_id)
    if db_stats:
        db_stats.total_xp = 0
        db_stats.level = 1
        db.commit()
        db.refresh(db_stats)
    return db_stats

# ===================== #
#  ANALYTICS / INSIGHTS OPERATIONS
# ===================== #

def get_user_activity_stats(db: Session, user_id: int):
    """Get comprehensive user activity statistics"""
    total_journals = db.query(models.Journal)\
                      .filter(models.Journal.user_id == user_id)\
                      .count()
    
    total_tasks = db.query(models.Task)\
                   .filter(models.Task.user_id == user_id)\
                   .count()
    
    completed_tasks = db.query(models.Task)\
                       .filter(models.Task.user_id == user_id, 
                              models.Task.is_completed == True)\
                       .count()
    
    user_stats = get_user_stats(db, user_id)
    
    return schemas.ActivityStats(
        total_journals=total_journals,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        completion_rate=(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        current_level=user_stats.level if user_stats else 1,
        total_xp=user_stats.total_xp if user_stats else 0
    )

def get_recent_activity(db: Session, user_id: int, days: int = 7):
    """Get recent user activity (journals and completed tasks)"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    recent_journals = db.query(models.Journal)\
                       .filter(models.Journal.user_id == user_id,
                              models.Journal.created_at >= cutoff_date)\
                       .order_by(models.Journal.created_at.desc())\
                       .all()
    
    # FIXED: Use completed_at for recent completed tasks
    recent_completed_tasks = db.query(models.Task)\
                            .filter(models.Task.user_id == user_id,
                                   models.Task.is_completed == True,
                                   models.Task.completed_at >= cutoff_date)\
                            .order_by(models.Task.completed_at.desc())\
                            .all()
    
    return schemas.RecentActivity(
        journals=recent_journals,
        completed_tasks=recent_completed_tasks,
        period_days=days
    )

# ===================== #
#  CATEGORY OPERATIONS
# ===================== #

def get_categories(db: Session):
    """Get all categories"""
    return db.query(models.Category).all()

def get_category(db: Session, category_id: int):
    """Get category by ID"""
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def create_category(db: Session, category: schemas.CategoryCreate):
    """Create a new category"""
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category