"""Simple user database (in-memory for demo, use real DB in production)"""

import json
import os
from typing import Optional, Dict
from backend.auth.jwt_handler import get_password_hash, verify_password

# Simple file-based user storage (replace with real database in production)
USERS_FILE = "users.json"


class UserDB:
    """Simple user database"""
    
    def __init__(self):
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """Load users from file"""
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_users(self):
        """Save users to file"""
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return self.users.get(username)
    
    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create new user"""
        if username in self.users:
            return False
        
        self.users[username] = {
            "username": username,
            "email": email,
            "hashed_password": get_password_hash(password),
            "is_active": True,
            "created_at": str(os.path.getmtime(__file__))
        }
        self._save_users()
        return True
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user"""
        user = self.get_user(username)
        if not user:
            return None
        
        if not verify_password(password, user["hashed_password"]):
            return None
        
        return user


# Global user database instance
user_db = UserDB()
