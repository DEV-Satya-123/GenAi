#!/usr/bin/env python3
"""
FastAPI Backend for AI Git Automation Agent
Clean architecture with proper separation of concerns
"""

from fastapi import FastAPI, WebSocket, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordRequestForm
from slowapi.errors import RateLimitExceeded
from datetime import timedelta
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
from backend.models.auth import UserRegister, UserLogin, Token, User
from backend.security.rate_limiter import limiter, rate_limit_exceeded_handler, RATE_LIMITS
from backend.security.error_handler import (
    validation_exception_handler,
    generic_exception_handler,
    http_exception_handler
)
from backend.security.validators import SecurityValidator
from backend.security.audit_logger import audit_logger
from backend.auth.jwt_handler import (
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from backend.auth.user_db import user_db

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


# ============= Authentication Endpoints =============

@app.post("/api/auth/register", response_model=User)
@limiter.limit("5/hour")
async def register(request: Request, user_data: UserRegister):
    """Register new user"""
    # Validate username
    if len(user_data.username) < 3 or len(user_data.username) > 50:
        raise HTTPException(
            status_code=400,
            detail="Username must be 3-50 characters"
        )
    
    # Validate password
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters"
        )
    
    if len(user_data.password) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password must be less than 72 characters"
        )
    
    # Create user
    success = user_db.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
    
    # Log registration
    ip = get_client_ip(request)
    audit_logger.log_event(
        event_type="user_registration",
        user_id=user_data.username,
        ip_address=ip,
        success=True
    )
    
    return User(
        username=user_data.username,
        email=user_data.email,
        is_active=True
    )


@app.post("/api/auth/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user and return JWT token"""
    # Authenticate user
    user = user_db.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        # Log failed login
        ip = get_client_ip(request)
        audit_logger.log_event(
            event_type="login_failed",
            user_id=form_data.username,
            ip_address=ip,
            success=False
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )
    
    # Log successful login
    ip = get_client_ip(request)
    audit_logger.log_event(
        event_type="login_success",
        user_id=user["username"],
        ip_address=ip,
        success=True
    )
    
    return Token(access_token=access_token, token_type="bearer")


@app.get("/api/auth/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    user = user_db.get_user(current_user["username"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(
        username=user["username"],
        email=user["email"],
        is_active=user["is_active"]
    )


# ============= Protected Endpoints =============

@app.get("/")
@limiter.limit(RATE_LIMITS["default"])
async def root(request: Request):
    """Root endpoint"""
    return {
        "message": "AI Git Automation API",
        "status": "running",
        "version": "1.0.0",
        "authentication": "enabled"
    }


@app.get("/api/status", response_model=StatusResponse)
@limiter.limit(RATE_LIMITS["status"])
async def get_status(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get current repository status"""
    return await repo_service.get_status()


@app.get("/api/repositories")
@limiter.limit(RATE_LIMITS["default"])
async def get_repositories(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get list of all repositories"""
    return await repo_service.get_repositories()


@app.post("/api/clone-to-path")
@limiter.limit(RATE_LIMITS["clone"])
async def clone_to_path_repository(
    request: Request,
    clone_request: CloneToPathRequest,
    current_user: dict = Depends(get_current_user)
):
    """Clone a Git repository to a specific path"""
    git_url = SecurityValidator.validate_git_url(clone_request.git_url)
    clone_path = SecurityValidator.validate_file_path(clone_request.clone_to_path)
    
    if clone_request.name:
        name = SecurityValidator.validate_repo_name(clone_request.name)
        clone_request.name = name
    
    clone_request.git_url = git_url
    clone_request.clone_to_path = clone_path
    
    ip = get_client_ip(request)
    audit_logger.log_clone(git_url, ip)
    
    return await repo_service.clone_to_path(clone_request, ws_manager)


@app.post("/api/clone")
@limiter.limit(RATE_LIMITS["clone"])
async def clone_repository(
    request: Request,
    clone_request: CloneRequest,
    current_user: dict = Depends(get_current_user)
):
    """Clone a Git repository to managed directory"""
    git_url = SecurityValidator.validate_git_url(clone_request.git_url)
    
    if clone_request.name:
        name = SecurityValidator.validate_repo_name(clone_request.name)
        clone_request.name = name
    
    clone_request.git_url = git_url
    
    ip = get_client_ip(request)
    audit_logger.log_clone(git_url, ip)
    
    return await repo_service.clone_repository(clone_request, ws_manager)


@app.post("/api/add-local")
@limiter.limit(RATE_LIMITS["default"])
async def add_local_repository(
    request: Request,
    add_request: AddLocalRequest,
    current_user: dict = Depends(get_current_user)
):
    """Add an existing local Git repository"""
    local_path = SecurityValidator.validate_file_path(add_request.local_path)
    
    if add_request.name:
        name = SecurityValidator.validate_repo_name(add_request.name)
        add_request.name = name
    
    add_request.local_path = local_path
    
    return await repo_service.add_local_repository(add_request, ws_manager)


@app.post("/api/set-active-repo")
@limiter.limit(RATE_LIMITS["default"])
async def set_active_repository(
    request: Request,
    set_request: SetActiveRepoRequest,
    current_user: dict = Depends(get_current_user)
):
    """Set the active repository"""
    return await repo_service.set_active_repository(set_request, ws_manager)


@app.delete("/api/repository/{repo_id}")
@limiter.limit(RATE_LIMITS["default"])
async def delete_repository(
    request: Request,
    repo_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a repository"""
    return await repo_service.delete_repository(repo_id, ws_manager)


@app.post("/api/run", response_model=RunResponse)
@limiter.limit(RATE_LIMITS["run"])
async def run_agent(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Run the automation agent"""
    return await repo_service.run_agent(ws_manager)


@app.post("/api/approve")
@limiter.limit(RATE_LIMITS["default"])
async def handle_approval(
    request: Request,
    approval_request: ApprovalRequest,
    current_user: dict = Depends(get_current_user)
):
    """Handle approval responses"""
    if approval_request.commit_message:
        commit_message = SecurityValidator.validate_commit_message(approval_request.commit_message)
        approval_request.commit_message = commit_message
        
        ip = get_client_ip(request)
        audit_logger.log_commit(
            repo_service.current_repo_path or "unknown",
            commit_message,
            ip
        )
    
    return await repo_service.handle_approval(approval_request, ws_manager)


@app.get("/api/workflow/{thread_id}/status")
@limiter.limit(RATE_LIMITS["default"])
async def get_workflow_status(
    request: Request,
    thread_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get workflow status"""
    return await repo_service.get_workflow_status(thread_id)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    from backend.services.websocket_service import handle_websocket
    await handle_websocket(websocket, ws_manager)


# ============= New Features: Search & Smart .gitignore =============

@app.get("/api/search-commits")
@limiter.limit(RATE_LIMITS["default"])
async def search_commits(
    request: Request,
    query: str,
    max_results: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Search commits by message, author, or content"""
    if not repo_service.current_repo_path:
        raise HTTPException(status_code=400, detail="No active repository")
    
    try:
        from tools.git_tools import GitTools
        git_tools = GitTools(repo_service.current_repo_path)
        results = git_tools.search_commits(query, max_results)
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/commit-history")
@limiter.limit(RATE_LIMITS["default"])
async def get_commit_history(
    request: Request,
    max_count: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get recent commit history"""
    if not repo_service.current_repo_path:
        raise HTTPException(status_code=400, detail="No active repository")
    
    try:
        from tools.git_tools import GitTools
        git_tools = GitTools(repo_service.current_repo_path)
        commits = git_tools.get_commit_history(max_count)
        
        return {
            "success": True,
            "commits": commits,
            "count": len(commits)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/gitignore-check")
@limiter.limit(RATE_LIMITS["default"])
async def check_gitignore(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Check .gitignore status and get recommendations"""
    if not repo_service.current_repo_path:
        raise HTTPException(status_code=400, detail="No active repository")
    
    try:
        from tools.git_tools import GitTools
        git_tools = GitTools(repo_service.current_repo_path)
        result = git_tools.smart_gitignore_check()
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/gitignore-fix")
@limiter.limit(RATE_LIMITS["default"])
async def fix_gitignore(
    request: Request,
    project_type: str = "python",
    current_user: dict = Depends(get_current_user)
):
    """Automatically fix .gitignore issues"""
    if not repo_service.current_repo_path:
        raise HTTPException(status_code=400, detail="No active repository")
    
    try:
        from tools.git_tools import GitTools
        git_tools = GitTools(repo_service.current_repo_path)
        result = git_tools.auto_fix_gitignore(project_type)
        
        # Notify via WebSocket
        await ws_manager.broadcast({
            "type": "gitignore_fixed",
            "data": result
        })
        
        return {
            "success": result['success'],
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Git Automation API...")
    print(f"📡 API: http://localhost:{settings.PORT}")
    print(f"📡 Docs: http://localhost:{settings.PORT}/docs")
    print("🔒 Security features enabled:")
    print("   ✓ JWT Authentication")
    print("   ✓ Rate limiting")
    print("   ✓ Input validation")
    print("   ✓ Audit logging")
    print("   ✓ Secure error handling")
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT, log_level="info")

async def check_gitignore(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Check .gitignore status and get recommendations"""
    if not repo_service.current_repo_path:
        raise HTTPException(status_code=400, detail="No active repository")
    
    try:
        from tools.git_tools import GitTools
        git_tools = GitTools(repo_service.current_repo_path)
        result = git_tools.smart_gitignore_check()
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/gitignore-fix")
@limiter.limit(RATE_LIMITS["default"])
async def fix_gitignore(
    request: Request,
    project_type: str = "python",
    current_user: dict = Depends(get_current_user)
):
    """Automatically fix .gitignore issues"""
    if not repo_service.current_repo_path:
        raise HTTPException(status_code=400, detail="No active repository")
    
    try:
        from tools.git_tools import GitTools
        git_tools = GitTools(repo_service.current_repo_path)
        result = git_tools.auto_fix_gitignore(project_type)
        
        # Notify via WebSocket
        await ws_manager.broadcast({
            "type": "gitignore_fixed",
            "data": result
        })
        
        return {
            "success": result['success'],
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
