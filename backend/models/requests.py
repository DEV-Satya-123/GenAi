"""Request models for API endpoints"""

from pydantic import BaseModel
from typing import Optional


class AddLocalRequest(BaseModel):
    """Request to add a local repository"""
    local_path: str
    name: Optional[str] = None


class CloneToPathRequest(BaseModel):
    """Request to clone repository to specific path"""
    git_url: str
    clone_to_path: str
    name: Optional[str] = None


class CloneRequest(BaseModel):
    """Request to clone repository to managed directory"""
    git_url: str
    name: Optional[str] = None


class SetActiveRepoRequest(BaseModel):
    """Request to set active repository"""
    repo_id: str


class ApprovalRequest(BaseModel):
    """Request for approval actions"""
    action: str
    commit_message: Optional[str] = None
    approval_type: Optional[str] = None
