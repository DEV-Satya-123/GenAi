"""Simple user database - Auto-selects PostgreSQL or JSON based on configuration"""

import os
from typing import Optional, Dict

# Check if PostgreSQL is configured
USE_POSTGRES = os.getenv("USE_POSTGRES", "true").lower() == "true"

if USE_POSTGRES:
    try:
        from backend.auth.user_db_postgres import UserDB
        print("✅ Using PostgreSQL for user authentication")
    except Exception as e:
        print(f"⚠️ PostgreSQL not available, falling back to JSON: {e}")
        from backend.auth.user_db_json import UserDB
else:
    from backend.auth.user_db_json import UserDB
    print("ℹ️ Using JSON files for user authentication")

# Global user database instance
user_db = UserDB()

