"""
Request Models
Pydantic models for validating incoming API requests
"""

from pydantic import BaseModel
from typing import Optional


class CloneToPathRequest(BaseModel):
    """
    Request model for cloning a Git repository to a specific path
    
    Attributes:
        git_url: The Git repository URL to clone
        clone_to_path: Local filesystem path where repository will be cloned
        name: Optional custom name for the repository
    """
    git_url: str
    clone_to_path: str
    name: Optional[str] = None


class AddLocalRequest(BaseModel):
    """
    Request model for adding an existing local Git repository
    
    Attributes:
        local_path: Path to existing Git repository on local filesystem
        name: Optional custom name for the repository
    """
    local_path: str
    name: Optional[str] = None


class CloneRequest(BaseModel):
    """
    Request model for cloning a Git repository (legacy format)
    
    Attributes:
        git_url: The Git repository URL to clone
        name: Optional custom name for the repository
    """
    git_url: str
    name: Optional[str] = None


class SetActiveRepoRequest(BaseModel):
    """
    Request model for setting the active repository
    
    Attributes:
        repo_id: Unique identifier of the repository to set as active
    """
    repo_id: str


class ApprovalRequest(BaseModel):
    """
    Request model for handling commit/push approval decisions
    
    Attributes:
        action: User action ('approve', 'reject', or 'edit')
        commit_message: Optional edited commit message
        approval_type: Type of approval ('commit' or 'push')
    """
    action: str
    commit_message: Optional[str] = None
    approval_type: Optional[str] = None