#!/usr/bin/env python3
"""
FastAPI Backend for AI Git Automation Agent
Provides REST API and WebSocket for real-time updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import sys
import os
import uuid
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    from agent_graph import GitAutomationAgent
    from config import REPO_PATH
    LANGGRAPH_AVAILABLE = True
    print("✅ LangGraph agent loaded successfully")
except ImportError as e:
    print(f"⚠️ LangGraph not available, creating simple fallback: {e}")
    # Create a simple fallback agent
    class GitAutomationAgent:
        def __init__(self, repo_path: str):
            from tools.git_tools import GitTools
            from llm.gemini_client import GeminiClient
            self.git_tools = GitTools(repo_path)
            self.gemini_client = GeminiClient()
        
        def run(self):
            result = {
                "has_changes": False,
                "diff": "",
                "commit_message": "",
                "approved": False,
                "committed": False,
                "push_approved": False,
                "pushed": False,
                "error": ""
            }
            
            try:
                # Simple workflow without interrupts
                has_changes = self.git_tools.has_changes()
                result["has_changes"] = has_changes
                
                if has_changes:
                    diff = self.git_tools.get_diff()
                    result["diff"] = diff
                    
                    commit_message = self.gemini_client.generate_commit_message(diff)
                    result["commit_message"] = commit_message
                    
                    # For now, just return the generated message
                    # The web UI will handle approvals later
                
                return result
            except Exception as e:
                result["error"] = str(e)
                return result
    
    from config import REPO_PATH
    LANGGRAPH_AVAILABLE = False
    print("✅ Simple fallback agent created")

# Global variables to track current workflow
current_agent = None
current_thread_id = None
current_repo_path = REPO_PATH  # Initialize with default repo path

# Repository management
CLONED_REPOS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cloned-repos")
REPOS_CONFIG_FILE = os.path.join(CLONED_REPOS_DIR, "repos.json")

# Ensure cloned repos directory exists
os.makedirs(CLONED_REPOS_DIR, exist_ok=True)


def load_repositories():
    """Load repository list from config file"""
    if os.path.exists(REPOS_CONFIG_FILE):
        try:
            with open(REPOS_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_repositories(repos):
    """Save repository list to config file"""
    with open(REPOS_CONFIG_FILE, 'w') as f:
        json.dump(repos, f, indent=2)


app = FastAPI(
    title="AI Git Automation API",
    description="Backend API for AI-powered Git automation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.active_agent = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass
    
    def set_active_agent(self, agent):
        self.active_agent = agent
    
    def handle_approval(self, approval_data: dict):
        if self.active_agent:
            self.active_agent.handle_approval_response(approval_data)


ws_manager = WebSocketManager()


class StatusResponse(BaseModel):
    has_changes: bool
    current_branch: str
    repo_path: str
    timestamp: str


class RunResponse(BaseModel):
    success: bool
    message: str
    result: Optional[dict] = None


class CloneRequest(BaseModel):
    git_url: str
    name: str = None


class SetActiveRepoRequest(BaseModel):
    repo_id: str


class ApprovalRequest(BaseModel):
    action: str
    commit_message: str = None
    approval_type: str = None


@app.get("/")
async def root():
    return {
        "message": "AI Git Automation API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Get current repository status"""
    try:
        agent = GitAutomationAgent(REPO_PATH)
        has_changes = agent.git_tools.has_changes()
        branch = agent.git_tools.get_current_branch()
        
        return StatusResponse(
            has_changes=has_changes,
            current_branch=branch,
            repo_path=REPO_PATH,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        print(f"Error in get_status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@app.get("/api/repositories")
async def get_repositories():
    """Get list of all cloned repositories"""
    try:
        repos = load_repositories()
        global current_repo_path
        
        # Add current active repo info
        for repo_id, repo_info in repos.items():
            repo_info["is_active"] = repo_info["path"] == current_repo_path
            
            # Check if repo still exists
            if os.path.exists(repo_info["path"]):
                repo_info["exists"] = True
                # Get current branch and changes
                try:
                    from tools.git_tools import GitTools
                    git_tools = GitTools(repo_info["path"])
                    repo_info["current_branch"] = git_tools.get_current_branch()
                    repo_info["has_changes"] = git_tools.has_changes()
                except:
                    repo_info["current_branch"] = "unknown"
                    repo_info["has_changes"] = False
            else:
                repo_info["exists"] = False
        
        return {
            "success": True,
            "repositories": repos,
            "active_repo_path": current_repo_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clone")
async def clone_repository(request: CloneRequest):
    """Clone a Git repository"""
    try:
        git_url = request.git_url.strip()
        
        # Extract repo name from URL
        if request.name:
            repo_name = request.name
        else:
            repo_name = git_url.split('/')[-1].replace('.git', '')
        
        # Create unique repo ID
        repo_id = f"{repo_name}_{uuid.uuid4().hex[:8]}"
        repo_path = os.path.join(CLONED_REPOS_DIR, repo_id)
        
        await ws_manager.broadcast({
            "type": "clone_started",
            "message": f"Cloning repository: {git_url}"
        })
        
        # Clone the repository
        try:
            result = subprocess.run(
                ["git", "clone", git_url, repo_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")
            
            # Save repository info
            repos = load_repositories()
            repos[repo_id] = {
                "id": repo_id,
                "name": repo_name,
                "git_url": git_url,
                "path": repo_path,
                "cloned_at": datetime.now().isoformat(),
                "is_active": False
            }
            save_repositories(repos)
            
            await ws_manager.broadcast({
                "type": "clone_complete",
                "message": f"Repository cloned successfully: {repo_name}",
                "repo_id": repo_id
            })
            
            return {
                "success": True,
                "message": "Repository cloned successfully",
                "repo_id": repo_id,
                "repo_path": repo_path
            }
            
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=408, detail="Clone operation timed out")
        except Exception as e:
            # Clean up failed clone
            if os.path.exists(repo_path):
                import shutil
                shutil.rmtree(repo_path, ignore_errors=True)
            raise HTTPException(status_code=500, detail=f"Clone failed: {str(e)}")
            
    except Exception as e:
        await ws_manager.broadcast({
            "type": "clone_error",
            "message": f"Clone failed: {str(e)}"
        })
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/set-active-repo")
async def set_active_repository(request: SetActiveRepoRequest):
    """Set the active repository for the agent"""
    try:
        repos = load_repositories()
        
        if request.repo_id not in repos:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        repo_info = repos[request.repo_id]
        
        if not os.path.exists(repo_info["path"]):
            raise HTTPException(status_code=404, detail="Repository path does not exist")
        
        # Update global current repo path
        global current_repo_path
        current_repo_path = repo_info["path"]
        
        # Update active status in repos
        for repo_id, repo_data in repos.items():
            repo_data["is_active"] = (repo_id == request.repo_id)
        save_repositories(repos)
        
        await ws_manager.broadcast({
            "type": "active_repo_changed",
            "message": f"Active repository changed to: {repo_info['name']}",
            "repo_id": request.repo_id,
            "repo_path": current_repo_path
        })
        
        return {
            "success": True,
            "message": "Active repository updated",
            "active_repo": repo_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/repository/{repo_id}")
async def delete_repository(repo_id: str):
    """Delete a cloned repository"""
    try:
        repos = load_repositories()
        
        if repo_id not in repos:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        repo_info = repos[repo_id]
        
        # Don't delete if it's the active repo
        global current_repo_path
        if repo_info["path"] == current_repo_path:
            raise HTTPException(status_code=400, detail="Cannot delete active repository")
        
        # Remove directory
        if os.path.exists(repo_info["path"]):
            import shutil
            shutil.rmtree(repo_info["path"], ignore_errors=True)
        
        # Remove from config
        del repos[repo_id]
        save_repositories(repos)
        
        await ws_manager.broadcast({
            "type": "repo_deleted",
            "message": f"Repository deleted: {repo_info['name']}",
            "repo_id": repo_id
        })
        
        return {
            "success": True,
            "message": "Repository deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/run", response_model=RunResponse)
async def run_agent():
    """Run the automation agent with WebSocket interaction"""
    try:
        agent = GitAutomationAgent(REPO_PATH)
        
        # Store the agent globally for approval handling
        global current_agent, current_workflow_state
        current_agent = agent
        
        await ws_manager.broadcast({
            "type": "workflow_started",
            "message": "Starting AI Git Automation workflow..."
        })
        
        if LANGGRAPH_AVAILABLE:
            # Use agentic workflow - but for now, simulate the approval flow
            try:
                # Run until we get the commit message
                result = agent.run()
                current_workflow_state = result
                
                # If we have a commit message, show approval modal
                if result.get("commit_message") and not result.get("committed"):
                    await ws_manager.broadcast({
                        "type": "approval_required",
                        "approval_type": "commit_approval",
                        "data": {
                            "type": "commit_approval",
                            "commit_message": result["commit_message"],
                            "instruction": "Please approve, reject, or edit the commit message"
                        }
                    })
                    
                    return RunResponse(
                        success=True,
                        message="Workflow paused for commit approval",
                        result={"status": "awaiting_approval", "commit_message": result["commit_message"]}
                    )
                else:
                    await ws_manager.broadcast({
                        "type": "workflow_complete",
                        "message": "Workflow completed",
                        "result": result
                    })
                    
                    return RunResponse(
                        success=True,
                        message="Agent execution completed",
                        result=result
                    )
            except Exception as e:
                await ws_manager.broadcast({
                    "type": "workflow_error",
                    "message": str(e)
                })
                raise HTTPException(status_code=500, detail=str(e))
        else:
            # Use simple workflow
            result = agent.run()
            current_workflow_state = result
            
            # If we have a commit message, show approval modal
            if result.get("commit_message") and not result.get("committed"):
                await ws_manager.broadcast({
                    "type": "approval_required",
                    "approval_type": "commit_approval",
                    "data": {
                        "type": "commit_approval",
                        "commit_message": result["commit_message"],
                        "instruction": "Please approve, reject, or edit the commit message"
                    }
                })
                
                return RunResponse(
                    success=True,
                    message="Workflow paused for commit approval",
                    result={"status": "awaiting_approval", "commit_message": result["commit_message"]}
                )
            else:
                await ws_manager.broadcast({
                    "type": "workflow_complete",
                    "message": "Workflow completed",
                    "result": result
                })
                
                return RunResponse(
                    success=True,
                    message="Agent execution completed",
                    result=result
                )
        
    except Exception as e:
        await ws_manager.broadcast({
            "type": "workflow_error",
            "message": str(e)
        })
        raise HTTPException(status_code=500, detail=str(e))


# Global variables to track current workflow
current_agent = None
current_workflow_state = None


# Global variables to track current workflow
current_agent = None
current_thread_id = None
current_repo_path = REPO_PATH  # Initialize with default repo path

# Repository management
CLONED_REPOS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cloned-repos")
REPOS_CONFIG_FILE = os.path.join(CLONED_REPOS_DIR, "repos.json")

# Ensure cloned repos directory exists
os.makedirs(CLONED_REPOS_DIR, exist_ok=True)


def load_repositories():
    """Load repository list from config file"""
    if os.path.exists(REPOS_CONFIG_FILE):
        try:
            with open(REPOS_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_repositories(repos):
    """Save repository list to config file"""
    with open(REPOS_CONFIG_FILE, 'w') as f:
        json.dump(repos, f, indent=2)


class CloneRequest(BaseModel):
    git_url: str
    name: str = None


class SetActiveRepoRequest(BaseModel):
    repo_id: str


class ApprovalRequest(BaseModel):
    action: str
    commit_message: str = None
    approval_type: str = None


@app.post("/api/approve")
async def handle_approval(request: ApprovalRequest):
    """Handle approval responses from the frontend"""
    try:
        global current_agent, current_workflow_state
        
        print(f"🔔 Received approval request:")
        print(f"   Action: {request.action}")
        print(f"   Approval Type: {request.approval_type}")
        print(f"   Commit Message: {request.commit_message}")
        print(f"   Current State: {current_workflow_state}")
        
        if not current_agent or not current_workflow_state:
            raise HTTPException(status_code=400, detail="No active workflow to approve")
        
        print(f"🔔 Handling approval: {request.action} for {request.approval_type}")
        
        # Handle commit approval
        if request.approval_type == "commit":
            print("📝 Processing commit approval...")
            if request.action == "approve":
                # Update commit message if edited
                if request.commit_message:
                    current_workflow_state["commit_message"] = request.commit_message
                
                # Perform the commit
                await ws_manager.broadcast({
                    "type": "step_update",
                    "message": "Committing changes..."
                })
                
                # Stage and commit
                if not current_agent.git_tools.git_add_all():
                    raise HTTPException(status_code=500, detail="Failed to stage changes")
                
                if current_agent.git_tools.git_commit(current_workflow_state["commit_message"]):
                    current_workflow_state["committed"] = True
                    
                    await ws_manager.broadcast({
                        "type": "step_complete",
                        "message": "Changes committed successfully!"
                    })
                    
                    # Add a small delay before asking for push approval
                    await asyncio.sleep(1.5)
                    
                    # Now ask for push approval
                    await ws_manager.broadcast({
                        "type": "approval_required",
                        "approval_type": "push_approval",
                        "data": {
                            "type": "push_approval",
                            "commit_message": current_workflow_state["commit_message"],
                            "instruction": "Please approve or reject pushing to remote repository"
                        }
                    })
                    
                    print(f"🚀 Sent push approval request for: {current_workflow_state['commit_message']}")
                    
                    return {
                        "success": True,
                        "message": "Commit approved, awaiting push approval",
                        "result": {"status": "awaiting_push_approval"}
                    }
                else:
                    raise HTTPException(status_code=500, detail="Failed to commit changes")
            
            elif request.action == "reject":
                await ws_manager.broadcast({
                    "type": "workflow_complete",
                    "message": "Commit rejected by user"
                })
                
                # Clear workflow state
                current_agent = None
                current_workflow_state = None
                
                return {
                    "success": True,
                    "message": "Commit rejected",
                    "result": {"status": "rejected"}
                }
        
        # Handle push approval
        elif request.approval_type == "push" or request.approval_type == "push_approval":
            print("🚀 Processing push approval...")
            if request.action == "approve":
                print("✅ Push approved, starting push...")
                await ws_manager.broadcast({
                    "type": "step_update",
                    "message": "Pushing to remote repository..."
                })
                
                if current_agent.git_tools.git_push():
                    current_workflow_state["pushed"] = True
                    print("✅ Push completed successfully!")
                    
                    await ws_manager.broadcast({
                        "type": "workflow_complete",
                        "message": "Changes pushed successfully!",
                        "result": current_workflow_state
                    })
                    
                    # Clear workflow state
                    current_agent = None
                    current_workflow_state = None
                    
                    return {
                        "success": True,
                        "message": "Push completed successfully",
                        "result": current_workflow_state
                    }
                else:
                    print("❌ Push failed!")
                    raise HTTPException(status_code=500, detail="Failed to push changes")
            
            elif request.action == "reject":
                print("❌ Push rejected by user")
                await ws_manager.broadcast({
                    "type": "workflow_complete",
                    "message": "Push rejected by user. Changes are committed locally."
                })
                
                # Clear workflow state
                current_agent = None
                current_workflow_state = None
                
                return {
                    "success": True,
                    "message": "Push rejected, changes remain local",
                    "result": current_workflow_state
                }
        
        print(f"❌ Invalid approval state: {request.approval_type}")
        return {
            "success": False,
            "message": f"Invalid approval state: {request.approval_type}"
        }
        
    except Exception as e:
        print(f"💥 Error in handle_approval: {e}")
        await ws_manager.broadcast({
            "type": "workflow_error",
            "message": str(e)
        })
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflow/{thread_id}/status")
async def get_workflow_status(thread_id: str):
    """Get the current status of a workflow"""
    try:
        agent = GitAutomationAgent(REPO_PATH)
        
        state = agent.get_current_state(thread_id)
        if not state:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        pending = agent.get_pending_approval(thread_id)
        
        return {
            "thread_id": thread_id,
            "state": state,
            "pending_approval": pending,
            "is_paused": bool(pending)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Receive JSON data from client
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "approval_response":
                ws_manager.handle_approval(data.get("data", {}))
            elif data.get("type") == "ping":
                # Respond to ping with pong
                await websocket.send_json({"type": "pong"})
            else:
                # Echo back for testing
                await websocket.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Git Automation API...")
    print("📡 API: http://localhost:8000")
    print("📡 Docs: http://localhost:8000/docs")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"📁 Parent directory: {parent_dir}")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
