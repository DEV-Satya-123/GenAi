#!/usr/bin/env python3
"""
FastAPI Backend for AI Git Automation Agent
Clean architecture with proper separation of concerns
"""

from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from backend.services.websocket_service import ws_manager
from backend.services.repository_service import RepositoryService
from backend.utils.config import get_settings
from backend.models.requests import (
    AddLocalRequest,
    CloneToPathRequest,
    CloneRequest,
    SetActiveRepoRequest,
    ApprovalRequest
)
from backend.models.responses import StatusResponse, RunResponse
from backend.security.rate_limiter import limiter, rate_limit_exceeded_handler, RATE_LIMITS
from backend.security.error_handler import (
    validation_exception_handler,
    generic_exception_handler,
    http_exception_handler
)
from backend.security.validators import SecurityValidator
from backend.security.audit_logger import audit_logger

# Initialize settings
settings = get_settings()

# Initialize services
repo_service = RepositoryService()

# Create FastAPI app
app = FastAPI(
    title="AI Git Automation API",
    description="Backend API for AI-powered Git automation",
    version="1.0.0"
)

# Add rate limiter
app.state.limiter = limiter

# Add exception handlers
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    return request.client.host if request.client else "unknown"


@app.get("/")
@limiter.limit(RATE_LIMITS["default"])
async def root(request: Request):
    """Root endpoint"""
    return {
        "message": "AI Git Automation API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/api/status", response_model=StatusResponse)
@limiter.limit(RATE_LIMITS["status"])
async def get_status(request: Request):
    """Get current repository status"""
    return await repo_service.get_status()


@app.get("/api/repositories")
@limiter.limit(RATE_LIMITS["default"])
async def get_repositories(request: Request):
    """Get list of all repositories"""
    return await repo_service.get_repositories()


@app.post("/api/clone-to-path")
@limiter.limit(RATE_LIMITS["clone"])
async def clone_to_path_repository(request: Request, clone_request: CloneToPathRequest):
    """Clone a Git repository to a specific path"""
    # Validate inputs
    git_url = SecurityValidator.validate_git_url(clone_request.git_url)
    clone_path = SecurityValidator.validate_file_path(clone_request.clone_to_path)
    
    if clone_request.name:
        name = SecurityValidator.validate_repo_name(clone_request.name)
        clone_request.name = name
    
    clone_request.git_url = git_url
    clone_request.clone_to_path = clone_path
    
    # Log attempt
    ip = get_client_ip(request)
    audit_logger.log_clone(git_url, ip)
    
    return await repo_service.clone_to_path(clone_request, ws_manager)


@app.post("/api/clone")
@limiter.limit(RATE_LIMITS["clone"])
async def clone_repository(request: Request, clone_request: CloneRequest):
    """Clone a Git repository to managed directory"""
    # Validate inputs
    git_url = SecurityValidator.validate_git_url(clone_request.git_url)
    
    if clone_request.name:
        name = SecurityValidator.validate_repo_name(clone_request.name)
        clone_request.name = name
    
    clone_request.git_url = git_url
    
    # Log attempt
    ip = get_client_ip(request)
    audit_logger.log_clone(git_url, ip)
    
    return await repo_service.clone_repository(clone_request, ws_manager)


@app.post("/api/add-local")
@limiter.limit(RATE_LIMITS["default"])
async def add_local_repository(request: Request, add_request: AddLocalRequest):
    """Add an existing local Git repository"""
    # Validate inputs
    local_path = SecurityValidator.validate_file_path(add_request.local_path)
    
    if add_request.name:
        name = SecurityValidator.validate_repo_name(add_request.name)
        add_request.name = name
    
    add_request.local_path = local_path
    
    return await repo_service.add_local_repository(add_request, ws_manager)


@app.post("/api/set-active-repo")
@limiter.limit(RATE_LIMITS["default"])
async def set_active_repository(request: Request, set_request: SetActiveRepoRequest):
    """Set the active repository"""
    return await repo_service.set_active_repository(set_request, ws_manager)


@app.delete("/api/repository/{repo_id}")
@limiter.limit(RATE_LIMITS["default"])
async def delete_repository(request: Request, repo_id: str):
    """Delete a repository"""
    return await repo_service.delete_repository(repo_id, ws_manager)


@app.post("/api/run", response_model=RunResponse)
@limiter.limit(RATE_LIMITS["run"])
async def run_agent(request: Request):
    """Run the automation agent"""
    return await repo_service.run_agent(ws_manager)


@app.post("/api/approve")
@limiter.limit(RATE_LIMITS["default"])
async def handle_approval(request: Request, approval_request: ApprovalRequest):
    """Handle approval responses"""
    # Validate commit message if provided
    if approval_request.commit_message:
        commit_message = SecurityValidator.validate_commit_message(approval_request.commit_message)
        approval_request.commit_message = commit_message
        
        # Log commit
        ip = get_client_ip(request)
        audit_logger.log_commit(
            repo_service.current_repo_path or "unknown",
            commit_message,
            ip
        )
    
    return await repo_service.handle_approval(approval_request, ws_manager)


@app.get("/api/workflow/{thread_id}/status")
@limiter.limit(RATE_LIMITS["default"])
async def get_workflow_status(request: Request, thread_id: str):
    """Get workflow status"""
    return await repo_service.get_workflow_status(thread_id)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    from backend.services.websocket_service import handle_websocket
    await handle_websocket(websocket, ws_manager)


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Git Automation API...")
    print(f"📡 API: http://localhost:{settings.PORT}")
    print(f"📡 Docs: http://localhost:{settings.PORT}/docs")
    print("🔒 Security features enabled:")
    print("   ✓ Rate limiting")
    print("   ✓ Input validation")
    print("   ✓ Audit logging")
    print("   ✓ Secure error handling")
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT, log_level="info")
