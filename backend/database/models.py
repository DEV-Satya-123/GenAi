"""SQLAlchemy database models"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.connection import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    repositories = relationship("Repository", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class Repository(Base):
    """Repository model"""
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(String(100), unique=True, nullable=False, index=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    git_url = Column(String(500), nullable=False)
    path = Column(String(1000), nullable=False)
    is_active = Column(Boolean, default=False)
    is_local = Column(Boolean, default=False)
    is_clone_to_path = Column(Boolean, default=False)
    current_branch = Column(String(100))
    has_changes = Column(Boolean, default=False)
    exists = Column(Boolean, default=True)
    cloned_at = Column(DateTime(timezone=True), server_default=func.now())
    last_checked = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="repositories")
    commits = relationship("Commit", back_populates="repository", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Repository(name='{self.name}', path='{self.path}')>"


class Commit(Base):
    """Commit history model"""
    __tablename__ = "commits"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    commit_hash = Column(String(40), nullable=False, index=True)
    short_hash = Column(String(7), nullable=False)
    message = Column(Text, nullable=False)
    author_name = Column(String(100), nullable=False)
    author_email = Column(String(100), nullable=False)
    committed_at = Column(DateTime(timezone=True), nullable=False)
    files_changed = Column(Integer, default=0)
    insertions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    commit_type = Column(String(20))  # bug_fix, feature, refactor, docs, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    repository = relationship("Repository", back_populates="commits")

    def __repr__(self):
        return f"<Commit(hash='{self.short_hash}', message='{self.message[:50]}')>"


class AuditLog(Base):
    """Audit log model for tracking user actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(JSON)  # Store additional event data as JSON
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(event='{self.event_type}', user_id={self.user_id})>"


class RepositoryStatistics(Base):
    """Cached repository statistics"""
    __tablename__ = "repository_statistics"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False, unique=True)
    total_commits = Column(Integer, default=0)
    total_contributors = Column(Integer, default=0)
    total_branches = Column(Integer, default=0)
    total_files = Column(Integer, default=0)
    active_days = Column(Integer, default=0)
    health_score = Column(Integer, default=0)
    health_rating = Column(String(20))
    first_commit_date = Column(DateTime(timezone=True))
    last_commit_date = Column(DateTime(timezone=True))
    languages = Column(JSON)  # Store language breakdown as JSON
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<RepositoryStatistics(repo_id={self.repository_id}, health={self.health_score})>"
