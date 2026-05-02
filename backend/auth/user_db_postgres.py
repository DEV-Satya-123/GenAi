"""PostgreSQL-based user database"""

from typing import Optional, Dict
from backend.database.connection import get_db_context
from backend.database.crud import (
    create_user as db_create_user,
    get_user_by_username,
    authenticate_user as db_authenticate_user
)


class UserDB:
    """PostgreSQL user database"""
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        with get_db_context() as db:
            user = get_user_by_username(db, username)
            if user:
                return {
                    "username": user.username,
                    "email": user.email,
                    "hashed_password": user.password_hash,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
            return None
    
    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create new user"""
        try:
            with get_db_context() as db:
                # Check if user exists
                existing = get_user_by_username(db, username)
                if existing:
                    return False
                
                # Create user
                db_create_user(db, username, email, password)
                return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user"""
        try:
            with get_db_context() as db:
                user = db_authenticate_user(db, username, password)
                if user:
                    return {
                        "username": user.username,
                        "email": user.email,
                        "hashed_password": user.password_hash,
                        "is_active": user.is_active,
                        "created_at": user.created_at.isoformat() if user.created_at else None
                    }
                return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None


# Global user database instance
user_db = UserDB()
