import os
from typing import Dict, Any, List, Optional, ClassVar, Union, Generator
from pydantic import BaseModel, Field
from psnawp_api import PSNAWP
from psnawp_api.models import User as PSNUser
from functools import lru_cache
try:
    # For region information
    import pycountry
    HAS_PYCOUNTRY = True
except ImportError:
    HAS_PYCOUNTRY = False

class PSNClient:
    """Singleton client for PSNAWP API"""
    _instance: ClassVar[Optional['PSNClient']] = None
    _client: PSNAWP

    def __new__(cls):
        if cls._instance is None:
            npsso = os.getenv("NPSSO")
            if not npsso:
                raise ValueError("NPSSO environment variable must be set")
            cls._instance = super(PSNClient, cls).__new__(cls)
            cls._instance._client = PSNAWP(npsso)
        return cls._instance

    @property
    def client(self) -> PSNAWP:
        return self._client

class PSNUserProfile(BaseModel):
    """Pydantic model for a PlayStation Network user profile"""
    online_id: str
    _user: Optional[PSNUser] = None
    _profile_data: Optional[Dict[str, Any]] = None
    _presence_data: Optional[Dict[str, Any]] = None
    _friendship_data: Optional[Dict[str, Any]] = None
    _trophy_summary_data: Optional[Any] = None
    _account_id: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def user(self) -> PSNUser:
        """Get or fetch the PSNUser object"""
        if self._user is None:
            try:
                # Direct instance is more reliable than the singleton
                psnawp_client = PSNAWP(os.getenv("NPSSO"))
                self._user = psnawp_client.user(online_id=self.online_id)
                self._account_id = self._user.account_id
            except Exception as e:
                print(f"Error fetching user {self.online_id}: {str(e)}")
                raise
        return self._user

    @property
    def account_id(self) -> str:
        """Get the user's account ID"""
        if self._account_id is None:
            self._account_id = self.user.account_id
        return self._account_id

    @property
    def profile(self) -> Dict[str, Any]:
        """Get or fetch the user profile"""
        if self._profile_data is None:
            try:
                self._profile_data = self.user.profile()
            except Exception as e:
                print(f"Error fetching profile for {self.online_id}: {str(e)}")
                self._profile_data = {}
        return self._profile_data

    @property
    def presence(self) -> Dict[str, Any]:
        """Get or fetch the user presence data"""
        if self._presence_data is None:
            try:
                self._presence_data = self.user.get_presence()
            except Exception as e:
                print(f"Error fetching presence for {self.online_id}: {str(e)}")
                self._presence_data = {}
        return self._presence_data
    
    @property
    def friendship(self) -> Dict[str, Any]:
        """Get or fetch the friendship data"""
        if self._friendship_data is None:
            try:
                self._friendship_data = self.user.friendship()
            except Exception as e:
                print(f"Error fetching friendship for {self.online_id}: {str(e)}")
                self._friendship_data = {}
        return self._friendship_data

    @property
    def trophy_summary(self) -> Any:
        """Get the user's trophy summary using the direct method"""
        if self._trophy_summary_data is None:
            try:
                self._trophy_summary_data = self.user.trophy_summary()
            except Exception as e:
                print(f"Error fetching trophy summary for {self.online_id}: {str(e)}")
                self._trophy_summary_data = {}
        return self._trophy_summary_data

    # Basic profile information
    def get_about_me(self) -> str:
        """Get the user's about me text"""
        return self.profile.get("aboutMe", "")
    
    def get_avatars(self) -> List[Dict[str, str]]:
        """Get the user's avatars"""
        return self.profile.get("avatars", [])
        
    def get_languages(self) -> List[str]:
        """Get the user's languages"""
        return self.profile.get("languages", [])
    
    def get_is_plus(self) -> bool:
        """Check if the user has PlayStation Plus"""
        return self.profile.get("isPlus", False)
    
    def get_is_officially_verified(self) -> bool:
        """Check if the user is officially verified"""
        return self.profile.get("isOfficiallyVerified", False)
    
    def get_account_id(self) -> str:
        """Get the user's PSN account ID"""
        return self.account_id
    
    def get_np_id(self) -> str:
        """Get the user's NP ID"""
        # This is not directly available in the standard API methods,
        # so we'll return empty as it's not crucial
        return ""
    
    # Presence information
    def get_online_status(self) -> str:
        """Get the user's online status"""
        try:
            return self.presence.get("primaryPlatformInfo", {}).get("onlineStatus", "")
        except Exception:
            return ""
    
    def get_platform(self) -> str:
        """Get the user's current platform"""
        try:
            return self.presence.get("primaryPlatformInfo", {}).get("platform", "")
        except Exception:
            return ""
    
    def get_last_online_date(self) -> str:
        """Get when the user was last online"""
        try:
            return self.presence.get("primaryPlatformInfo", {}).get("lastOnlineDate", "")
        except Exception:
            return ""
    
    def get_availability(self) -> str:
        """Get the user's availability status"""
        try:
            return self.presence.get("availability", "")
        except Exception:
            return ""
    
    # Friendship information
    def get_friends_count(self) -> int:
        """Get the user's friend count"""
        try:
            return self.friendship.get("friendsCount", 0)
        except Exception:
            return 0

    def get_mutual_friends_count(self) -> int:
        """Get mutual friends count"""
        try:
            return self.friendship.get("mutualFriendsCount", 0)
        except Exception:
            return 0
            
    def get_friend_relation(self) -> str:
        """Get the friendship relation with this user"""
        try:
            return self.friendship.get("friendRelation", "")
        except Exception:
            return ""
    
    # Access methods to check blocking/following status
    def get_is_blocking(self) -> bool:
        """Check if you are blocking this user"""
        try:
            return self.user.is_blocked()
        except Exception:
            return False
    
    def get_is_following(self) -> bool:
        """This info isn't directly available through PSNAWP API"""
        return False
    
    # Trophy information - using direct methods
    def get_trophy_level(self) -> int:
        """Get the user's trophy level"""
        try:
            trophy_data = self.trophy_summary
            return trophy_data.trophy_level
        except Exception:
            return 0
    
    def get_trophy_progress(self) -> int:
        """Get the user's trophy progress"""
        try:
            trophy_data = self.trophy_summary
            return trophy_data.progress
        except Exception:
            return 0
    
    def get_trophy_tier(self) -> int:
        """Get the user's trophy tier"""
        try:
            trophy_data = self.trophy_summary
            return trophy_data.tier
        except Exception:
            return 0
    
    def get_earned_trophies(self) -> Dict[str, int]:
        """Get the user's earned trophies"""
        try:
            trophy_data = self.trophy_summary
            earned = trophy_data.earned_trophies
            return {
                "platinum": earned.platinum,
                "gold": earned.gold,
                "silver": earned.silver,
                "bronze": earned.bronze
            }
        except Exception:
            return {"platinum": 0, "gold": 0, "silver": 0, "bronze": 0}
    
    # Pass-through methods for more advanced trophy functions
    def get_trophy_titles(self, limit=None):
        """Get user's trophy titles"""
        try:
            return self.user.trophy_titles(limit=limit)
        except Exception as e:
            print(f"Error fetching trophy titles: {str(e)}")
            return []
    
    def get_trophy_titles_for_title(self, title_ids):
        """Get user's trophy titles for specific titles"""
        try:
            return self.user.trophy_titles_for_title(title_ids=title_ids)
        except Exception as e:
            print(f"Error fetching trophy titles for title: {str(e)}")
            return []
    
    def get_trophies(self, np_communication_id, platform, include_progress=False):
        """Get trophies for a specific game"""
        try:
            return self.user.trophies(
                np_communication_id=np_communication_id,
                platform=platform,
                include_progress=include_progress
            )
        except Exception as e:
            print(f"Error fetching trophies: {str(e)}")
            return []
    
    def get_title_stats(self, limit=None):
        """Get detailed information about games the user has played
        
        Returns information about play time, play count, and other stats
        for each game title the user has played.
        """
        try:
            return self.user.title_stats(limit=limit)
        except Exception as e:
            print(f"Error fetching title stats: {str(e)}")
            return []
    
    # Construct full profile object
    def get_full_profile(self) -> Dict[str, Any]:
        """Get a complete profile with all available information"""
        profile = {
            # Basic info
            "online_id": self.online_id,
            "account_id": self.get_account_id(),
            "about_me": self.get_about_me(),
            "avatars": self.get_avatars(),
            "languages": self.get_languages(),
            "is_plus": self.get_is_plus(),
            "is_officially_verified": self.get_is_officially_verified(),
            
            # Presence information
            "online_status": self.get_online_status(),
            "platform": self.get_platform(),
            "last_online": self.get_last_online_date(),
            "availability": self.get_availability(),
            
            # Friendship information
            "friends_count": self.get_friends_count(),
            "mutual_friends_count": self.get_mutual_friends_count(),
            "friend_relation": self.get_friend_relation(),
            "is_blocking": self.get_is_blocking(),
            
            # Trophy information
            "trophy_level": self.get_trophy_level(),
            "trophy_progress": self.get_trophy_progress(),
            "trophy_tier": self.get_trophy_tier(),
            "earned_trophies": self.get_earned_trophies(),
        }
        
        # Clean up the profile by removing empty/zero values
        return {k: v for k, v in profile.items() if v or v == 0 or v == False}

@lru_cache(maxsize=100)
def get_psn_user(online_id: str) -> PSNUserProfile:
    """Get a PSN user profile (cached)"""
    return PSNUserProfile(online_id=online_id)