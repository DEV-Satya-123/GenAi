"""CRUD operations for database models"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List
from datetime import datetime
import bcrypt

from backend.database.models import User, Repository, Commit, AuditLog, RepositoryStatistics


# ============= User CRUD =============

def create_user(db: Session, username: str, email: str, password: str) -> User:
    """Create a new user"""
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user = User(
        username=username,
        email=email,
        password_hash=password_hash
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    
    if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return user
    return None


# ============= Repository CRUD =============

def create_repository(db: Session, user_id: int, repo_data: dict) -> Repository:
    """Create a new repository"""
    repo = Repository(
        user_id=user_id,
        **repo_data
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


def get_repository_by_id(db: Session, repo_id: str) -> Optional[Repository]:
    """Get repository by repo_id (UUID)"""
    return db.query(Repository).filter(Repository.repo_id == repo_id).first()


def get_user_repositories(db: Session, user_id: int) -> List[Repository]:
    """Get all repositories for a user"""
    return db.query(Repository).filter(Repository.user_id == user_id).all()


def get_active_repository(db: Session, user_id: int) -> Optional[Repository]:
    """Get active repository for a user"""
    return db.query(Repository).filter(
        Repository.user_id == user_id,
        Repository.is_active == True
    ).first()


def set_active_repository(db: Session, user_id: int, repo_id: str) -> Repository:
    """Set a repository as active (deactivate others)"""
    # Deactivate all user repositories
    db.query(Repository).filter(Repository.user_id == user_id).update({"is_active": False})
    
    # Activate the selected repository
    repo = get_repository_by_id(db, repo_id)
    if repo and repo.user_id == user_id:
        repo.is_active = True
        db.commit()
        db.refresh(repo)
        return repo
    return None


def delete_repository(db: Session, repo_id: str, user_id: int) -> bool:
    """Delete a repository"""
    repo = db.query(Repository).filter(
        Repository.repo_id == repo_id,
        Repository.user_id == user_id
    ).first()
    
    if repo:
        db.delete(repo)
        db.commit()
        return True
    return False


# ============= Commit CRUD =============

def create_commit(db: Session, repository_id: int, commit_data: dict) -> Commit:
    """Create a new commit record"""
    commit = Commit(
        repository_id=repository_id,
        **commit_data
    )
    db.add(commit)
    db.commit()
    db.refresh(commit)
    return commit


def get_repository_commits(db: Session, repository_id: int, limit: int = 20) -> List[Commit]:
    """Get commits for a repository"""
    return db.query(Commit).filter(
        Commit.repository_id == repository_id
    ).order_by(desc(Commit.committed_at)).limit(limit).all()


def search_commits(db: Session, repository_id: int, query: str, limit: int = 10) -> List[Commit]:
    """Search commits by message"""
    return db.query(Commit).filter(
        Commit.repository_id == repository_id,
        Commit.message.ilike(f"%{query}%")
    ).order_by(desc(Commit.committed_at)).limit(limit).all()


# ============= Audit Log CRUD =============

def create_audit_log(db: Session, log_data: dict) -> AuditLog:
    """Create an audit log entry"""
    log = AuditLog(**log_data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_user_audit_logs(db: Session, user_id: int, limit: int = 100) -> List[AuditLog]:
    """Get audit logs for a user"""
    return db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(desc(AuditLog.created_at)).limit(limit).all()


# ============= Repository Statistics CRUD =============

def upsert_repository_statistics(db: Session, repository_id: int, stats_data: dict) -> RepositoryStatistics:
    """Create or update repository statistics"""
    stats = db.query(RepositoryStatistics).filter(
        RepositoryStatistics.repository_id == repository_id
    ).first()
    
    if stats:
        # Update existing
        for key, value in stats_data.items():
            setattr(stats, key, value)
    else:
        # Create new
        stats = RepositoryStatistics(
            repository_id=repository_id,
            **stats_data
        )
        db.add(stats)
    
    db.commit()
    db.refresh(stats)
    return stats


def get_repository_statistics(db: Session, repository_id: int) -> Optional[RepositoryStatistics]:
    """Get cached repository statistics"""
    return db.query(RepositoryStatistics).filter(
        RepositoryStatistics.repository_id == repository_id
    ).first()
