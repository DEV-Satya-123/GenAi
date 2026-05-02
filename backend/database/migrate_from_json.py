"""Migration script to move data from JSON files to PostgreSQL"""

import json
import os
from datetime import datetime
from pathlib import Path
from backend.database.connection import get_db_context, init_db
from backend.database.crud import create_user, create_repository


def get_json_file_paths():
    """Get paths to JSON files"""
    # Get project root directory
    project_root = Path(__file__).parent.parent.parent
    
    return {
        'users_file': project_root / 'users.json',
        'repos_file': project_root / 'cloned-repos' / 'repos.json'
    }


def migrate_users():
    """Migrate users from JSON to PostgreSQL"""
    paths = get_json_file_paths()
    users_file = paths['users_file']
    
    if not users_file.exists():
        print(f"⚠️ No users.json file found at {users_file}")
        return
    
    with open(users_file, 'r') as f:
        users_data = json.load(f)
    
    with get_db_context() as db:
        migrated = 0
        for username, user_data in users_data.items():
            try:
                # Check if user already exists
                from backend.database.crud import get_user_by_username
                existing = get_user_by_username(db, username)
                if existing:
                    print(f"⚠️ User '{username}' already exists, skipping")
                    continue
                
                # Create user (password_hash is already hashed in JSON)
                from backend.database.models import User
                
                # Handle created_at timestamp
                created_at = datetime.now()
                if 'created_at' in user_data:
                    try:
                        # Try ISO format first
                        created_at = datetime.fromisoformat(user_data['created_at'])
                    except (ValueError, TypeError):
                        # If that fails, try Unix timestamp
                        try:
                            created_at = datetime.fromtimestamp(float(user_data['created_at']))
                        except:
                            created_at = datetime.now()
                
                user = User(
                    username=username,
                    email=user_data.get('email', f'{username}@example.com'),
                    password_hash=user_data.get('hashed_password', user_data.get('password_hash', '')),
                    is_active=user_data.get('is_active', True),
                    created_at=created_at
                )
                db.add(user)
                db.commit()
                migrated += 1
                print(f"✅ Migrated user: {username}")
            except Exception as e:
                print(f"❌ Error migrating user {username}: {e}")
                db.rollback()
    
    print(f"\n✅ Migrated {migrated} users")


def migrate_repositories():
    """Migrate repositories from JSON to PostgreSQL"""
    paths = get_json_file_paths()
    repos_file = paths['repos_file']
    
    if not repos_file.exists():
        print(f"⚠️ No repos.json file found at {repos_file}")
        return
    
    with open(repos_file, 'r') as f:
        repos_data = json.load(f)
    
    with get_db_context() as db:
        # Get first user (or create default user)
        from backend.database.crud import get_user_by_username
        user = get_user_by_username(db, "admin")
        if not user:
            # Try to get any user
            from backend.database.models import User
            user = db.query(User).first()
            
        if not user:
            print("⚠️ No users found, creating default admin user")
            user = create_user(db, "admin", "admin@example.com", "admin123")
        
        migrated = 0
        for repo_id, repo_data in repos_data.items():
            try:
                # Check if repository already exists
                from backend.database.crud import get_repository_by_id
                existing = get_repository_by_id(db, repo_id)
                if existing:
                    print(f"⚠️ Repository '{repo_data['name']}' already exists, skipping")
                    continue
                
                # Create repository
                repo = create_repository(db, user.id, {
                    'repo_id': repo_id,
                    'name': repo_data['name'],
                    'git_url': repo_data['git_url'],
                    'path': repo_data['path'],
                    'is_active': repo_data.get('is_active', False),
                    'is_local': repo_data.get('is_local', False),
                    'is_clone_to_path': repo_data.get('is_clone_to_path', False),
                    'current_branch': repo_data.get('current_branch'),
                    'has_changes': repo_data.get('has_changes', False),
                    'exists': repo_data.get('exists', True),
                    'cloned_at': datetime.fromisoformat(repo_data['cloned_at'])
                })
                migrated += 1
                print(f"✅ Migrated repository: {repo_data['name']}")
            except Exception as e:
                print(f"❌ Error migrating repository {repo_data['name']}: {e}")
                db.rollback()
    
    print(f"\n✅ Migrated {migrated} repositories")


def run_migration():
    """Run full migration from JSON to PostgreSQL"""
    print("🚀 Starting migration from JSON to PostgreSQL...\n")
    
    # Initialize database (create tables)
    print("📊 Creating database tables...")
    init_db()
    print()
    
    # Migrate users
    print("👥 Migrating users...")
    migrate_users()
    print()
    
    # Migrate repositories
    print("📁 Migrating repositories...")
    migrate_repositories()
    print()
    
    print("✅ Migration completed successfully!")
    print("\n💡 Next steps:")
    print("   1. Update .env with DATABASE_URL")
    print("   2. Restart the backend server")
    print("   3. Test the application")
    print("   4. Backup JSON files (optional)")


if __name__ == "__main__":
    run_migration()
