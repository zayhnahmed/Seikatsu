"""
Health Sync Service
Future integration with Google Fit and Apple Health for fitness tracking.
Syncs activity data and rewards XP for workouts.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from services.xp_manager import add_xp

logger = logging.getLogger(__name__)

# XP rewards for different activity types
ACTIVITY_XP_REWARDS = {
    "walking": 5,      # per 1000 steps
    "running": 15,     # per km
    "cycling": 10,     # per km
    "swimming": 20,    # per 100m
    "workout": 30,     # per session
    "yoga": 25,        # per session
    "meditation": 20,  # per session
    "sleep": 10,       # for good sleep (7-9 hours)
}

# Fitness category ID (should match your Category table)
FITNESS_CATEGORY_ID = 2  # Adjust based on your category setup


class HealthSyncService:
    """Service for syncing health and fitness data."""
    
    def __init__(self):
        self.google_fit_api = None  # Would be initialized with credentials
        self.apple_health_api = None  # Would be initialized with credentials
    
    def calculate_activity_xp(self, activity_type: str, amount: float) -> int:
        """
        Calculate XP for a given activity.
        
        Args:
            activity_type: Type of activity (walking, running, etc.)
            amount: Amount of activity (steps, km, etc.)
            
        Returns:
            XP to award
        """
        base_xp = ACTIVITY_XP_REWARDS.get(activity_type.lower(), 5)
        
        if activity_type.lower() == "walking":
            # XP per 1000 steps
            return int((amount / 1000) * base_xp)
        elif activity_type.lower() in ["running", "cycling"]:
            # XP per km
            return int(amount * base_xp)
        elif activity_type.lower() == "swimming":
            # XP per 100m
            return int((amount / 100) * base_xp)
        else:
            # Session-based activities
            return base_xp


def sync_google_fit(
    db: Session,
    user_id: int,
    access_token: str,
    days_back: int = 1
) -> Dict:
    """
    Sync fitness data from Google Fit API.
    
    Args:
        db: Database session
        user_id: User ID
        access_token: Google Fit OAuth access token
        days_back: Number of days to sync (default: 1)
        
    Returns:
        Dictionary with sync results and XP awarded
    """
    try:
        # This is a placeholder implementation
        # Actual implementation requires:
        # 1. pip install google-auth google-auth-oauthlib google-auth-httplib2
        # 2. pip install google-api-python-client
        # 3. Google Cloud project with Fitness API enabled
        
        logger.info(f"Syncing Google Fit data for user {user_id}")
        
        # Example API call structure (commented out):
        """
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        
        credentials = Credentials(token=access_token)
        service = build('fitness', 'v1', credentials=credentials)
        
        # Define time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days_back)
        
        # Convert to milliseconds (Fitness API requirement)
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)
        
        # Fetch step count
        steps_response = service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId='derived:com.google.step_count.delta:com.google.android.gms:estimated_steps',
            datasetId=f'{start_ms}-{end_ms}'
        ).execute()
        
        # Fetch activity sessions
        sessions_response = service.users().sessions().list(
            userId='me',
            startTime=start_time.isoformat() + 'Z',
            endTime=end_time.isoformat() + 'Z'
        ).execute()
        """
        
        # Mock data for demonstration
        activities = [
            {"type": "walking", "amount": 8000, "date": datetime.utcnow()},
            {"type": "running", "amount": 5.2, "date": datetime.utcnow()},
        ]
        
        total_xp = 0
        synced_activities = []
        
        service = HealthSyncService()
        
        for activity in activities:
            xp = service.calculate_activity_xp(activity["type"], activity["amount"])
            
            # Award XP
            xp_result = add_xp(
                db=db,
                user_id=user_id,
                category_id=FITNESS_CATEGORY_ID,
                amount=xp,
                reason=f"Google Fit sync: {activity['type']} - {activity['amount']}"
            )
            
            total_xp += xp
            synced_activities.append({
                "type": activity["type"],
                "amount": activity["amount"],
                "xp_earned": xp,
                "date": activity["date"].isoformat()
            })
        
        logger.info(
            f"Synced {len(activities)} activities from Google Fit for user {user_id}, "
            f"awarded {total_xp} XP"
        )
        
        return {
            "success": True,
            "source": "Google Fit",
            "activities_synced": len(activities),
            "total_xp_earned": total_xp,
            "activities": synced_activities,
            "message": "Google Fit integration requires API setup"
        }
        
    except Exception as e:
        logger.error(f"Error syncing Google Fit for user {user_id}: {str(e)}")
        raise


def sync_apple_health(
    db: Session,
    user_id: int,
    health_data: Dict,
    days_back: int = 1
) -> Dict:
    """
    Sync fitness data from Apple Health.
    Note: Apple Health data must be sent from the iOS app (HealthKit).
    
    Args:
        db: Database session
        user_id: User ID
        health_data: Health data payload from iOS app
        days_back: Number of days to sync (default: 1)
        
    Returns:
        Dictionary with sync results and XP awarded
    """
    try:
        logger.info(f"Syncing Apple Health data for user {user_id}")
        
        # Apple Health data comes from the iOS app via HealthKit
        # The app must request permissions and send data to your API
        # Expected format:
        # {
        #     "steps": 10000,
        #     "distance": 5.5,  # km
        #     "active_energy": 350,  # calories
        #     "workouts": [
        #         {"type": "running", "duration": 30, "distance": 5.2}
        #     ],
        #     "sleep": {
        #         "duration": 7.5,  # hours
        #         "quality": "good"
        #     }
        # }
        
        total_xp = 0
        synced_activities = []
        service = HealthSyncService()
        
        # Process steps
        if "steps" in health_data:
            xp = service.calculate_activity_xp("walking", health_data["steps"])
            xp_result = add_xp(
                db=db,
                user_id=user_id,
                category_id=FITNESS_CATEGORY_ID,
                amount=xp,
                reason=f"Apple Health: {health_data['steps']} steps"
            )
            total_xp += xp
            synced_activities.append({
                "type": "steps",
                "amount": health_data["steps"],
                "xp_earned": xp
            })
        
        # Process workouts
        if "workouts" in health_data:
            for workout in health_data["workouts"]:
                workout_type = workout.get("type", "workout")
                amount = workout.get("distance", 1)  # Default to 1 session if no distance
                
                xp = service.calculate_activity_xp(workout_type, amount)
                xp_result = add_xp(
                    db=db,
                    user_id=user_id,
                    category_id=FITNESS_CATEGORY_ID,
                    amount=xp,
                    reason=f"Apple Health: {workout_type} workout"
                )
                total_xp += xp
                synced_activities.append({
                    "type": workout_type,
                    "amount": amount,
                    "xp_earned": xp
                })
        
        # Process sleep
        if "sleep" in health_data:
            duration = health_data["sleep"].get("duration", 0)
            # Reward good sleep (7-9 hours)
            if 7 <= duration <= 9:
                xp = ACTIVITY_XP_REWARDS["sleep"]
                xp_result = add_xp(
                    db=db,
                    user_id=user_id,
                    category_id=FITNESS_CATEGORY_ID,
                    amount=xp,
                    reason=f"Apple Health: {duration}h quality sleep"
                )
                total_xp += xp
                synced_activities.append({
                    "type": "sleep",
                    "amount": duration,
                    "xp_earned": xp
                })
        
        logger.info(
            f"Synced {len(synced_activities)} activities from Apple Health for user {user_id}, "
            f"awarded {total_xp} XP"
        )
        
        return {
            "success": True,
            "source": "Apple Health",
            "activities_synced": len(synced_activities),
            "total_xp_earned": total_xp,
            "activities": synced_activities
        }
        
    except Exception as e:
        logger.error(f"Error syncing Apple Health for user {user_id}: {str(e)}")
        raise


def get_fitness_summary(db: Session, user_id: int, days: int = 7) -> Dict:
    """
    Get fitness activity summary for a user.
    This would query synced fitness data from a FitnessActivity model.
    
    Args:
        db: Database session
        user_id: User ID
        days: Number of days to summarize (default: 7)
        
    Returns:
        Dictionary with fitness summary
    """
    try:
        # This requires a FitnessActivity model to store synced data
        # For now, returning a placeholder structure
        
        from services.xp_manager import get_user_level_details
        
        level_details = get_user_level_details(db, user_id)
        
        # Find fitness category
        fitness_data = None
        for cat in level_details.get("categories", []):
            if cat["category_id"] == FITNESS_CATEGORY_ID:
                fitness_data = cat
                break
        
        return {
            "period_days": days,
            "fitness_level": fitness_data["level"] if fitness_data else 1,
            "fitness_xp": fitness_data["xp"] if fitness_data else 0,
            "message": "Connect Google Fit or Apple Health to track fitness data",
            "connected_services": []
        }
        
    except Exception as e:
        logger.error(f"Error getting fitness summary for user {user_id}: {str(e)}")
        raise


def disconnect_health_service(
    db: Session,
    user_id: int,
    service: str
) -> Dict:
    """
    Disconnect a health tracking service.
    
    Args:
        db: Database session
        user_id: User ID
        service: Service to disconnect (google_fit or apple_health)
        
    Returns:
        Dictionary with disconnection status
    """
    try:
        # This would remove stored credentials/tokens
        # Requires a UserHealthConnection model
        
        logger.info(f"Disconnecting {service} for user {user_id}")
        
        return {
            "success": True,
            "service": service,
            "message": f"{service} disconnected successfully"
        }
        
    except Exception as e:
        logger.error(
            f"Error disconnecting {service} for user {user_id}: {str(e)}"
        )
        raise


# Integration guide for developers:
"""
To implement full health sync:

1. Google Fit Setup:
   - Create project in Google Cloud Console
   - Enable Fitness API
   - Create OAuth 2.0 credentials
   - Install: pip install google-auth google-api-python-client
   - Implement OAuth flow in your app

2. Apple Health Setup:
   - Add HealthKit capability in Xcode
   - Request permissions in iOS app
   - Use HealthKit framework to read data
   - Send data to backend API endpoint

3. Database Schema:
   Create FitnessActivity model:
   
   class FitnessActivity(Base):
       __tablename__ = "fitness_activities"
       
       id: int
       user_id: int
       activity_type: str
       amount: float
       xp_earned: int
       source: str  # google_fit, apple_health
       synced_at: datetime
       activity_date: datetime

4. Background Sync:
   - Set up scheduled task to sync daily
   - Store user tokens securely
   - Handle token refresh
   - Implement webhook listeners for real-time sync
"""