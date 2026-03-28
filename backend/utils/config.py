"""Configuration utilities and settings"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # CORS Settings
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # Repository Settings
    DEFAULT_REPO_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "cloned-repos"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


def get_config_paths():
    """Get standardized configuration paths"""
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    cloned_repos_dir = os.path.join(parent_dir, "cloned-repos")
    repos_config_file = os.path.join(cloned_repos_dir, "repos.json")
    
    os.makedirs(cloned_repos_dir, exist_ok=True)
    
    return {
        "cloned_repos_dir": cloned_repos_dir,
        "repos_config_file": repos_config_file
    }