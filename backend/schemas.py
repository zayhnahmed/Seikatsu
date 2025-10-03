from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ===================== #
#  JOURNAL SCHEMAS
# ===================== #
class JournalBase(BaseModel):
    title: str
    content: str
    mood: Optional[str] = None  # Added mood field to match model

class JournalCreate(JournalBase):
    pass

class JournalUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[str] = None


class Journal(JournalBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Updated for Pydantic v2

# ===================== #
#  TASK SCHEMAS
# ===================== #
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    xp_reward: Optional[int] = 10
    due_date: Optional[datetime] = None  # Added due_date to match model

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    xp_reward: Optional[int] = None
    due_date: Optional[datetime] = None


class Task(TaskBase):
    id: int
    user_id: int
    is_completed: bool
    completed_at: Optional[datetime] = None  # Added completed_at field
    created_at: datetime

    class Config:
        from_attributes = True

# ===================== #
#  USER STATS / XP SCHEMAS
# ===================== #
class UserStatsBase(BaseModel):
    level: int
    total_xp: int

class UserStats(UserStatsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class XPUpdate(BaseModel):
    xp_gained: int

class LevelProgress(BaseModel):
    current_level: int
    total_xp: int
    progress_in_current_level: int
    xp_needed_for_next_level: int
    progress_percentage: float
    current_level_threshold: int
    next_level_threshold: int

# ===================== #
#  CATEGORY SCHEMAS
# ===================== #
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# ===================== #
#  LEVEL SCHEMAS (per category)
# ===================== #
class LevelBase(BaseModel):
    level: int = 1
    xp: int = 0

class LevelCreate(LevelBase):
    category_id: int

class Level(LevelBase):
    id: int
    user_id: int
    category_id: int
    category: Category

    class Config:
        from_attributes = True

# ===================== #
#  AUTHENTICATION SCHEMAS
# ===================== #
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ===================== #
#  USER SCHEMAS
# ===================== #
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserWithStats(User):
    user_stats: Optional[UserStats] = None

# ===================== #
#  ANALYTICS / INSIGHTS SCHEMAS
# ===================== #
class ActivityStats(BaseModel):
    total_journals: int
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    current_level: int
    total_xp: int

class RecentActivity(BaseModel):
    journals: list[Journal]
    completed_tasks: list[Task]
    period_days: int

class InsightsSummary(BaseModel):
    total_journal_entries: int
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    message: str

class Streaks(BaseModel):
    journal_streak: int
    task_completion_streak: int
    message: str

# ===================== #
#  RESPONSE SCHEMAS
# ===================== #
class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None

class HealthCheck(BaseModel):
    status: str
    service: str
    timestamp: datetime

class VersionInfo(BaseModel):
    version: str
    app: str