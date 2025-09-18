"""
XP Marketplace & Theme Management Routes
Handles XP marketplace, theme purchases, and rewards system
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import crud
import schemas
from deps import get_db, get_current_user

router = APIRouter()

@router.get("/items", response_model=List[schemas.MarketplaceItem])
def get_marketplace_items(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get all available marketplace items"""
    try:
        items = crud.get_marketplace_items(db, category=category)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching marketplace items: {str(e)}")

@router.get("/themes", response_model=List[schemas.Theme])
def get_available_themes(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get all available themes"""
    try:
        themes = crud.get_available_themes(db)
        user_themes = crud.get_user_themes(db, user_id=current_user.id)
        
        # Mark themes as owned/purchased
        for theme in themes:
            theme.is_owned = any(ut.theme_id == theme.id for ut in user_themes)
            
        return themes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching themes: {str(e)}")

@router.post("/purchase/{item_id}")
def purchase_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Purchase a marketplace item with XP"""
    try:
        # Get item details
        item = crud.get_marketplace_item(db, item_id=item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Check if user already owns the item
        if crud.user_owns_item(db, user_id=current_user.id, item_id=item_id):
            raise HTTPException(status_code=400, detail="You already own this item")
        
        # Get user stats to check XP balance
        user_stats = crud.get_user_stats(db, user_id=current_user.id)
        if not user_stats or user_stats.total_xp < item.xp_cost:
            raise HTTPException(status_code=400, detail="Insufficient XP")
        
        # Process purchase
        purchase = crud.process_purchase(db, user_id=current_user.id, item_id=item_id)
        
        return {
            "message": "Purchase successful!",
            "item_name": item.name,
            "xp_spent": item.xp_cost,
            "remaining_xp": user_stats.total_xp - item.xp_cost,
            "purchase_id": purchase.id,
            "purchased_at": purchase.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Purchase failed: {str(e)}")

@router.post("/themes/purchase/{theme_id}")
def purchase_theme(
    theme_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Purchase a theme with XP"""
    try:
        theme = crud.get_theme(db, theme_id=theme_id)
        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")
        
        # Check if user already owns the theme
        if crud.user_owns_theme(db, user_id=current_user.id, theme_id=theme_id):
            raise HTTPException(status_code=400, detail="You already own this theme")
        
        # Check XP balance
        user_stats = crud.get_user_stats(db, user_id=current_user.id)
        if not user_stats or user_stats.total_xp < theme.xp_cost:
            raise HTTPException(status_code=400, detail="Insufficient XP")
        
        # Process theme purchase
        user_theme = crud.purchase_theme(db, user_id=current_user.id, theme_id=theme_id)
        
        return {
            "message": "Theme purchased successfully!",
            "theme_name": theme.name,
            "xp_spent": theme.xp_cost,
            "remaining_xp": user_stats.total_xp - theme.xp_cost,
            "can_activate": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Theme purchase failed: {str(e)}")

@router.get("/my-items", response_model=List[schemas.UserPurchase])
def get_my_purchases(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get all items purchased by current user"""
    try:
        purchases = crud.get_user_purchases(db, user_id=current_user.id)
        return purchases
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching purchases: {str(e)}")

@router.get("/my-themes", response_model=List[schemas.UserTheme])
def get_my_themes(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get all themes owned by current user"""
    try:
        user_themes = crud.get_user_themes(db, user_id=current_user.id)
        return user_themes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user themes: {str(e)}")

@router.put("/themes/activate/{theme_id}")
def activate_theme(
    theme_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Activate a purchased theme"""
    try:
        # Check if user owns the theme
        if not crud.user_owns_theme(db, user_id=current_user.id, theme_id=theme_id):
            raise HTTPException(status_code=403, detail="You don't own this theme")
        
        # Activate the theme
        crud.activate_user_theme(db, user_id=current_user.id, theme_id=theme_id)
        
        theme = crud.get_theme(db, theme_id=theme_id)
        return {
            "message": "Theme activated successfully!",
            "active_theme": theme.name,
            "theme_id": theme_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error activating theme: {str(e)}")

@router.get("/active-theme", response_model=schemas.Theme)
def get_active_theme(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get currently active theme for user"""
    try:
        active_theme = crud.get_active_user_theme(db, user_id=current_user.id)
        if not active_theme:
            # Return default theme
            return crud.get_default_theme(db)
        return active_theme.theme
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting active theme: {str(e)}")

@router.get("/rewards/daily")
def get_daily_reward(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Claim daily XP reward (placeholder)"""
    try:
        # Check if user already claimed today's reward
        if crud.has_claimed_daily_reward(db, user_id=current_user.id):
            raise HTTPException(status_code=400, detail="Daily reward already claimed")
        
        # Award daily reward XP
        daily_xp = 50  # Base daily reward
        crud.update_user_xp(db, user_id=current_user.id, xp_gained=daily_xp)
        
        # Mark daily reward as claimed
        crud.mark_daily_reward_claimed(db, user_id=current_user.id)
        
        return {
            "message": "Daily reward claimed!",
            "xp_gained": daily_xp,
            "next_claim_available": "24 hours"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error claiming daily reward: {str(e)}")

@router.get("/leaderboard")
def get_xp_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get XP leaderboard (placeholder)"""
    if limit > 50:
        limit = 50  # Prevent large requests
    
    try:
        leaderboard = crud.get_xp_leaderboard(db, limit=limit)
        user_rank = crud.get_user_xp_rank(db, user_id=current_user.id)
        
        return {
            "leaderboard": leaderboard,
            "your_rank": user_rank,
            "total_users": crud.get_total_users_count(db),
            "note": "Leaderboard updates every hour"
        }
        
    except Exception as e:
        return {
            "message": "Leaderboard temporarily unavailable",
            "leaderboard": [],
            "your_rank": None,
            "error": str(e)
        }

@router.get("/special-offers")
def get_special_offers(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get special marketplace offers (placeholder)"""
    return {
        "message": "Special offers coming soon!",
        "current_offers": [],
        "upcoming_features": [
            "Limited-time theme discounts",
            "XP multiplier events", 
            "Seasonal item collections",
            "Achievement-based rewards"
        ]
    }

@router.get("/stats")
def get_marketplace_stats(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get user's marketplace statistics"""
    try:
        user_stats = crud.get_user_stats(db, user_id=current_user.id)
        purchase_count = crud.get_user_purchase_count(db, user_id=current_user.id)
        theme_count = crud.get_user_theme_count(db, user_id=current_user.id)
        
        return {
            "current_xp": user_stats.total_xp if user_stats else 0,
            "current_level": user_stats.level if user_stats else 1,
            "total_purchases": purchase_count,
            "owned_themes": theme_count,
            "lifetime_xp_spent": crud.get_lifetime_xp_spent(db, user_id=current_user.id),
            "achievement_level": crud.calculate_spender_achievement_level(db, user_id=current_user.id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting marketplace stats: {str(e)}")