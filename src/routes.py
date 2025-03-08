from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from typing import List, Dict, Any, Optional, Set
from _psnawp import get_psn_user, PSNUserProfile
from pydantic import BaseModel, Field

# Create router with API prefix and tags for better documentation
router = APIRouter(
    prefix="/api",
    tags=["api"]
)

# Available fields that can be requested
AVAILABLE_USER_FIELDS = {
    # Basic info
    "online_id", "account_id", "about_me", "avatars", 
    "languages", "is_plus", "is_officially_verified",
    
    # Presence information
    "online_status", "platform", "last_online", "availability",
    
    # Friendship information
    "friends_count", "mutual_friends_count", "friend_relation",
    "is_blocking", 
    
    # Trophy information
    "trophy_level", "trophy_progress", "trophy_tier", "earned_trophies",
}

class UserRequest(BaseModel):
    """Model for requesting user data with specific fields"""
    online_id: str
    fields: Optional[List[str]] = Field(
        default=None, 
        description="Specific fields to include in response. Omit for all fields."
    )

class BatchUserRequest(BaseModel):
    """Model for requesting data for multiple users"""
    users: List[UserRequest]

# Dependency to get a PSN user profile
async def get_psn_profile(
    online_id: str = Path(..., description="PlayStation Network ID")
) -> PSNUserProfile:
    """Dependency that retrieves a PSN user profile"""
    try:
        return get_psn_user(online_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User not found: {str(e)}")

# Get API status
@router.get("/status")
async def api_status():
    """Check API status"""
    return {
        "status": "online",
        "version": "1.0"
    }

@router.get("/users/{online_id}")
async def get_user_profile(
    online_id: str = Path(..., description="PlayStation Network ID"),
    fields: Optional[List[str]] = Query(
        None, 
        description="Specific fields to include in response (comma-separated). Omit for all fields."
    ),
):
    """
    Get a user's PSN profile with field selection.
    
    - Specify fields as a comma-separated list to get only those fields
    - Omit fields parameter to get all available information
    
    Available fields:
    - Basic info: online_id, account_id, about_me, avatars, languages, is_plus, is_officially_verified
    - Presence: online_status, platform, last_online, availability
    - Friendship: friends_count, mutual_friends_count, friend_relation, is_blocking
    - Trophies: trophy_level, trophy_progress, trophy_tier, earned_trophies
    """
    try:
        user = get_psn_user(online_id)
        
        # Get all profile data
        profile = user.get_full_profile()
        
        # Filter fields if specified
        if fields:
            valid_fields = [f for f in fields if f in AVAILABLE_USER_FIELDS]
            return {k: profile[k] for k in valid_fields if k in profile}
        
        return profile
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User not found: {str(e)}")

# Shortcut endpoints for common data
@router.get("/users/{online_id}/basic")
async def get_user_basic_info(online_id: str):
    """Get basic user information (online_id, about_me, avatars)"""
    try:
        user = get_psn_user(online_id)
        profile = user.get_full_profile()
        return {
            "online_id": profile["online_id"],
            "about_me": profile["about_me"],
            "avatars": profile["avatars"]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User not found: {str(e)}")

@router.get("/users/{online_id}/presence")
async def get_user_presence(online_id: str):
    """Get user's online presence information"""
    try:
        user = get_psn_user(online_id)
        profile = user.get_full_profile()
        return {
            "online_id": profile["online_id"],
            "online_status": profile["online_status"],
            "platform": profile["platform"],
            "last_online": profile["last_online"],
            "availability": profile["availability"]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User not found: {str(e)}")

@router.get("/users/{online_id}/friends")
async def get_user_friends_info(online_id: str):
    """Get information about a user's friends"""
    try:
        user = get_psn_user(online_id)
        profile = user.get_full_profile()
        return {
            "online_id": profile["online_id"],
            "friends_count": profile["friends_count"],
            "mutual_friends_count": profile["mutual_friends_count"],
            "friend_relation": profile["friend_relation"]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User not found: {str(e)}")

@router.get("/users/{online_id}/trophies")
async def get_user_trophies(online_id: str):
    """Get user's trophy information"""
    try:
        user = get_psn_user(online_id)
        profile = user.get_full_profile()
        return {
            "online_id": profile["online_id"],
            "trophy_level": profile["trophy_level"],
            "trophy_progress": profile["trophy_progress"],
            "trophy_tier": profile.get("trophy_tier", 0),
            "earned_trophies": profile["earned_trophies"]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User not found: {str(e)}")

@router.post("/users/batch")
async def batch_get_users(
    request: BatchUserRequest = Body(..., description="Batch request for multiple users")
):
    """
    Get information for multiple users in a single request.
    
    For each user, you can specify which fields to include.
    
    Available fields:
    - Basic info: online_id, account_id, about_me, avatars, languages, is_plus, is_officially_verified
    - Presence: online_status, platform, last_online, availability
    - Friendship: friends_count, mutual_friends_count, friend_relation, is_blocking
    - Trophies: trophy_level, trophy_progress, trophy_tier, earned_trophies
    """
    results = []
    
    for user_req in request.users:
        try:
            user = get_psn_user(user_req.online_id)
            profile = user.get_full_profile()
            
            # Filter fields if specified
            if user_req.fields:
                valid_fields = [f for f in user_req.fields if f in AVAILABLE_USER_FIELDS]
                results.append({k: profile[k] for k in valid_fields if k in profile})
            else:
                results.append(profile)
                
        except Exception:
            # Add a placeholder for users that couldn't be found
            results.append({
                "online_id": user_req.online_id,
                "error": "User not found"
            })
    
    return results

# Search endpoint
@router.get("/users")
async def search_users(
    query: str = Query(..., description="PSN ID to search for"),
    fields: Optional[List[str]] = Query(
        None, 
        description="Specific fields to include in response (comma-separated). Omit for all fields."
    ),
):
    """
    Search for PSN users with field selection
    
    Available fields:
    - Basic info: online_id, account_id, about_me, avatars, languages, is_plus, is_officially_verified
    - Presence: online_status, platform, last_online, availability
    - Friendship: friends_count, mutual_friends_count, friend_relation, is_blocking
    - Trophies: trophy_level, trophy_progress, trophy_tier, earned_trophies
    """
    try:
        user = get_psn_user(query)
        profile = user.get_full_profile()
        
        # Filter fields if specified
        if fields:
            valid_fields = [f for f in fields if f in AVAILABLE_USER_FIELDS]
            return [{k: profile[k] for k in valid_fields if k in profile}]
        
        return [profile]
    except Exception:
        return []

@router.get("/users/{online_id}/raw-profile")
async def get_user_raw_profile(online_id: str):
    """
    Get the raw profile data directly from the PSN API.
    
    This returns the unprocessed profile data as provided by the PSNAWP library.
    """
    try:
        user = get_psn_user(online_id)
        return user.profile
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User not found: {str(e)}")

@router.get("/users/{online_id}/trophy-titles")
async def get_trophy_titles(
    online_id: str,
    limit: Optional[int] = Query(None, description="Max number of titles to retrieve")
):
    """
    Get the user's trophy titles (games they have trophies for)
    
    This endpoint returns the list of games for which the user has earned trophies.
    It supports limiting the number of titles returned.
    """
    try:
        user = get_psn_user(online_id)
        trophy_titles = user.get_trophy_titles(limit=limit)
        
        # Return titles in a list format
        title_list = []
        for title in trophy_titles:
            try:
                title_list.append({
                    "title_id": title.title_id,
                    "title_name": title.title_name,
                    "platform": str(title.platform),
                    "trophies_earned": title.earned_trophies.total,
                    "trophies_total": title.defined_trophies.total,
                    "progress": title.progress
                })
            except Exception as e:
                print(f"Error processing title: {e}")
        
        return {
            "online_id": online_id,
            "total_titles": len(title_list),
            "titles": title_list
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not retrieve trophy titles: {str(e)}")

@router.get("/users/{online_id}/games")
async def get_played_games(
    online_id: str,
    limit: Optional[int] = Query(None, description="Max number of games to retrieve")
):
    """
    Get a list of games the user has played with detailed statistics
    
    This endpoint returns game-related statistics including:
    - Title name and ID
    - Platform category
    - Image URL
    - Play count
    - First played date
    - Last played date
    - Play duration
    """
    try:
        user = get_psn_user(online_id)
        title_iterator = user.get_title_stats(limit=limit)
        
        # Return game data in a list format
        game_list = []
        for title in title_iterator:
            try:
                game_list.append({
                    "name": title.name,
                    "title_id": title.title_id,
                    "platform": title.category,
                    "image_url": title.image_url,
                    "play_count": title.play_count,
                    "first_played": title.first_played_date_time,
                    "last_played": title.last_played_date_time,
                    "play_duration": str(title.play_duration)
                })
            except Exception as e:
                print(f"Error processing game: {e}")
        
        return {
            "online_id": online_id,
            "total_games": len(game_list),
            "games": game_list
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not retrieve game stats: {str(e)}")