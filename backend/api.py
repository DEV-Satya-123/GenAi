#!/usr/bin/env python3
"""
FastAPI Backend for AI Git Automation Agent
Clean architecture with proper separation of concerns
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Git Automation API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Get current repository status"""
    return await repo_service.get_status()


@app.get("/api/repositories")
async def get_repositories():
    """Get list of all repositories"""
    return await repo_service.get_repositories()


@app.post("/api/clone-to-path")
async def clone_to_path_repository(request: CloneToPathRequest):
    """Clone a Git repository to a specific path"""
    return await repo_service.clone_to_path(request, ws_manager)


@app.post("/api/clone")
async def clone_repository(request: CloneRequest):
    """Clone a Git repository to managed directory"""
    return await repo_service.clone_repository(request, ws_manager)


@app.post("/api/add-local")
async def add_local_repository(request: AddLocalRequest):
    """Add an existing local Git repository"""
    return await repo_service.add_local_repository(request, ws_manager)


@app.post("/api/set-active-repo")
async def set_active_repository(request: SetActiveRepoRequest):
    """Set the active repository"""
    return await repo_service.set_active_repository(request, ws_manager)


@app.delete("/api/repository/{repo_id}")
async def delete_repository(repo_id: str):
    """Delete a repository"""
    return await repo_service.delete_repository(repo_id, ws_manager)


@app.post("/api/run", response_model=RunResponse)
async def run_agent():
    """Run the automation agent"""
    return await repo_service.run_agent(ws_manager)


@app.post("/api/approve")
async def handle_approval(request: ApprovalRequest):
    """Handle approval responses"""
    return await repo_service.handle_approval(request, ws_manager)


@app.get("/api/workflow/{thread_id}/status")
async def get_workflow_status(thread_id: str):
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
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT, log_level="info")
