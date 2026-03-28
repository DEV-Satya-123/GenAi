"""
Response Models
Pydantic models for API response validation and documentation
"""

from pydantic import BaseModel
from typing import Optional


class StatusResponse(BaseModel):
    """
    Response model for repository status information
    
    Attributes:
        has_changes: Whether repository has uncommitted changes
        current_branch: Name of the currently checked out branch
        repo_path: Filesystem path to the repository
        timestamp: ISO format timestamp of status check
    """
    has_changes: bool
    current_branch: str
    repo_path: str
    timestamp: str


class RunResponse(BaseModel):
    """
    Response model for workflow execution results
    
    Attributes:
        success: Whether the workflow executed successfully
        message: Human-readable status message
        result: Optional dictionary containing workflow results
    """
    success: bool
    message: str
    result: Optional[dict] = None