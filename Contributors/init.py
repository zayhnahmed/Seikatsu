"""
Routes module for Seikatsu Backend
This module contains all API route definitions organized by feature
"""

from fastapi import APIRouter
from . import journal, users, auth, insights, market

# Create main router
api_router = APIRouter()

# Include all route modules
api_router.include_router(
    journal.router,
    prefix="/journal",
    tags=["journal"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    insights.router,
    prefix="/insights",
    tags=["analytics"]
)

api_router.include_router(
    market.router,
    prefix="/market",
    tags=["marketplace"]
)

__all__ = ["api_router"]