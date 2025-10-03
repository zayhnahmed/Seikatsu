"""
Market Routes - XP Marketplace for Gamification
Handles item listings, purchases, and user inventory
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

import crud
import schemas
from database import get_db
from logger import logger

router = APIRouter(
    prefix="/market",
    tags=["Market"]
)


# ===================== #
#  MARKET ITEM SCHEMAS
# ===================== #
class MarketItemBase(BaseModel):
    name: str
    description: str
    xp_cost: int
    item_type: str  # "theme", "boost", "perk", "cosmetic"
    rarity: str = "common"  # "common", "rare", "epic", "legendary"
    icon: str = "🎁"


class MarketItem(MarketItemBase):
    id: int
    is_available: bool = True
    
    class Config:
        from_attributes = True


class PurchaseRequest(BaseModel):
    user_id: int


class PurchaseResponse(BaseModel):
    message: str
    item: MarketItem
    remaining_xp: int
    user_level: int


class UserInventoryItem(BaseModel):
    item_id: int
    item_name: str
    item_type: str
    purchased_at: str
    is_equipped: bool = False


# ===================== #
#  MOCK MARKET ITEMS
#  (In production, these would be stored in database)
# ===================== #
MARKET_ITEMS = [
    {
        "id": 1,
        "name": "Dark Mode Theme",
        "description": "Sleek dark theme for your dashboard",
        "xp_cost": 100,
        "item_type": "theme",
        "rarity": "common",
        "icon": "🌙",
        "is_available": True
    },
    {
        "id": 2,
        "name": "Ocean Breeze Theme",
        "description": "Calming blue and teal color scheme",
        "xp_cost": 150,
        "item_type": "theme",
        "rarity": "rare",
        "icon": "🌊",
        "is_available": True
    },
    {
        "id": 3,
        "name": "2x XP Boost (1 Week)",
        "description": "Double XP for all activities for 7 days",
        "xp_cost": 500,
        "item_type": "boost",
        "rarity": "epic",
        "icon": "⚡",
        "is_available": True
    },
    {
        "id": 4,
        "name": "Productivity Perk",
        "description": "Unlock advanced task management features",
        "xp_cost": 300,
        "item_type": "perk",
        "rarity": "rare",
        "icon": "🎯",
        "is_available": True
    },
    {
        "id": 5,
        "name": "Golden Crown Badge",
        "description": "Show off your dedication with this exclusive badge",
        "xp_cost": 1000,
        "item_type": "cosmetic",
        "rarity": "legendary",
        "icon": "👑",
        "is_available": True
    },
    {
        "id": 6,
        "name": "Forest Green Theme",
        "description": "Nature-inspired green theme",
        "xp_cost": 120,
        "item_type": "theme",
        "rarity": "common",
        "icon": "🌲",
        "is_available": True
    },
    {
        "id": 7,
        "name": "Focus Mode Perk",
        "description": "Distraction-free journaling experience",
        "xp_cost": 250,
        "item_type": "perk",
        "rarity": "rare",
        "icon": "🎧",
        "is_available": True
    },
    {
        "id": 8,
        "name": "Cherry Blossom Theme",
        "description": "Beautiful pink and white sakura theme",
        "xp_cost": 200,
        "item_type": "theme",
        "rarity": "rare",
        "icon": "🌸",
        "is_available": True
    },
    {
        "id": 9,
        "name": "Streak Freeze",
        "description": "Protect your streak for one missed day",
        "xp_cost": 400,
        "item_type": "boost",
        "rarity": "epic",
        "icon": "❄️",
        "is_available": True
    },
    {
        "id": 10,
        "name": "Diamond Avatar Frame",
        "description": "Prestigious diamond-encrusted avatar border",
        "xp_cost": 1500,
        "item_type": "cosmetic",
        "rarity": "legendary",
        "icon": "💎",
        "is_available": True
    }
]


# ===================== #
#  ROUTE HANDLERS
# ===================== #
@router.get("/items", response_model=List[MarketItem])
async def get_market_items(
    item_type: Optional[str] = None,
    rarity: Optional[str] = None,
    max_cost: Optional[int] = None
):
    """
    List all available items in the marketplace.
    
    Optional filters:
    - **item_type**: Filter by type (theme, boost, perk, cosmetic)
    - **rarity**: Filter by rarity (common, rare, epic, legendary)
    - **max_cost**: Only show items within XP budget
    """
    try:
        items = MARKET_ITEMS.copy()
        
        # Apply filters
        if item_type:
            items = [item for item in items if item["item_type"] == item_type.lower()]
        
        if rarity:
            items = [item for item in items if item["rarity"] == rarity.lower()]
        
        if max_cost is not None:
            items = [item for item in items if item["xp_cost"] <= max_cost]
        
        # Only return available items
        items = [item for item in items if item.get("is_available", True)]
        
        logger.info(f"Fetched {len(items)} market items with filters: type={item_type}, rarity={rarity}, max_cost={max_cost}")
        return items
    
    except Exception as e:
        logger.error(f"Error fetching market items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch market items"
        )


@router.get("/items/{item_id}", response_model=MarketItem)
async def get_market_item(item_id: int):
    """
    Get details of a specific market item.
    """
    try:
        item = next((item for item in MARKET_ITEMS if item["id"] == item_id), None)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        
        if not item.get("is_available", True):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item is no longer available"
            )
        
        return item
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch item"
        )


@router.post("/buy/{item_id}", response_model=PurchaseResponse)
async def purchase_item(
    item_id: int,
    purchase: PurchaseRequest,
    db: Session = Depends(get_db)
):
    """
    Purchase an item from the marketplace using XP.
    
    Process:
    1. Validate user exists and has sufficient XP
    2. Deduct XP cost from user's balance
    3. Add item to user's inventory (mock implementation)
    4. Return purchase confirmation
    """
    try:
        # Find the item
        item = next((item for item in MARKET_ITEMS if item["id"] == item_id), None)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found"
            )
        
        if not item.get("is_available", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item is no longer available"
            )
        
        # Verify user exists
        user = crud.get_user(db, purchase.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {purchase.user_id} not found"
            )
        
        # Get user's current XP
        user_stats = crud.get_user_stats(db, purchase.user_id)
        if not user_stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User stats not found"
            )
        
        # Check if user has enough XP
        if user_stats.total_xp < item["xp_cost"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient XP. Required: {item['xp_cost']}, Available: {user_stats.total_xp}"
            )
        
        # Deduct XP from user (negative XP gain)
        updated_stats = crud.update_user_xp(db, purchase.user_id, -item["xp_cost"])
        
        # TODO: In production, save purchase to user_inventory table
        # For now, we just log the purchase
        logger.info(
            f"User {purchase.user_id} purchased '{item['name']}' for {item['xp_cost']} XP. "
            f"Remaining XP: {updated_stats.total_xp}, Level: {updated_stats.level}"
        )
        
        return PurchaseResponse(
            message=f"Successfully purchased {item['name']}!",
            item=MarketItem(**item),
            remaining_xp=updated_stats.total_xp,
            user_level=updated_stats.level
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error purchasing item {item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete purchase"
        )


@router.get("/user/{user_id}/inventory", response_model=List[UserInventoryItem])
async def get_user_inventory(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all items owned by a user.
    
    **Note**: This is a mock implementation. In production, this would
    query a user_inventory table in the database.
    """
    try:
        # Verify user exists
        user = crud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        # TODO: In production, query actual user_inventory table
        # For now, return empty inventory
        logger.info(f"Fetching inventory for user {user_id}")
        
        return []  # Empty inventory (mock)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching inventory for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user inventory"
        )


@router.get("/user/{user_id}/affordable", response_model=List[MarketItem])
async def get_affordable_items(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all items that the user can afford based on their current XP.
    """
    try:
        # Verify user exists and get their stats
        user = crud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        user_stats = crud.get_user_stats(db, user_id)
        if not user_stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User stats not found"
            )
        
        # Filter items by user's XP
        affordable_items = [
            item for item in MARKET_ITEMS 
            if item["xp_cost"] <= user_stats.total_xp and item.get("is_available", True)
        ]
        
        logger.info(
            f"User {user_id} can afford {len(affordable_items)} items "
            f"with {user_stats.total_xp} XP"
        )
        
        return affordable_items
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching affordable items for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch affordable items"
        )