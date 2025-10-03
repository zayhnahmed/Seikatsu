"""
Routes Package Initialization
Aggregates all API routers for the Seikatsu application
"""
from fastapi import APIRouter
from .journal import router as journal_router
from .tasks import router as tasks_router
from .insights import router as insights_router
from .auth import router as auth_router
from .market import router as market_router
from .users import router as user_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers with their prefixes and tags
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    user_router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    journal_router,
    prefix="/journals",
    tags=["Journals"]
)

api_router.include_router(
    tasks_router,
    prefix="/tasks",
    tags=["Tasks"]
)

api_router.include_router(
    insights_router,
    prefix="/insights",
    tags=["Insights & Analytics"]
)

api_router.include_router(
    market_router,
    prefix="/market",
    tags=["XP Marketplace"]
)

__all__ = ["api_router"]