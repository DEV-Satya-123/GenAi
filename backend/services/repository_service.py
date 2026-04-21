"""Repository Service - Handles all repository and workflow operations"""

import os
import json
import uuid
import subprocess
import shutil
import stat
import asyncio
from datetime import datetime
from typing import Dict, Optional
from fastapi import HTTPException

from backend.utils.config import get_config_paths


class RepositoryService:
    """Service for managing Git repositories and workflows"""
    
    def __init__(self):
        """Initialize repository service"""
        paths = get_config_paths()
        self.repos_dir = paths["cloned_repos_dir"]
        self.config_file = paths["repos_config_file"]
        self.current_repo_path = None
        self.current_agent = None
        self.current_workflow_state = None
        
        # Ensure directories exist
        os.makedirs(self.repos_dir, exist_ok=True)
        
        # Load active repository on startup
        self._load_active_repository()
    
    def _load_repositories(self) -> Dict:
        """Load repository configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_repositories(self, repos: Dict):
        """Save repository configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(repos, f, indent=2)
    
    def _load_active_repository(self):
        """Load the active repository on startup"""
        repos = self._load_repositories()
        for repo_id, repo_data in repos.items():
            if repo_data.get('is_active', False):
                repo_path = repo_data.get('path')
                if repo_path and os.path.exists(repo_path):
                    self.current_repo_path = repo_path
                    print(f"✅ Loaded active repository: {repo_path}")
                    return
        print("ℹ️ No active repository found")
    
    def _get_agent(self, repo_path: str):
        """Get or create agent instance"""
        try:
            from agent_graph import GitAutomationAgent
            return GitAutomationAgent(repo_path)
        except ImportError:
            # Fallback agent
            from tools.git_tools import GitTools
            from llm.gemini_client import GeminiClient
            
            class FallbackAgent:
                def __init__(self, repo_path: str):
                    self.git_tools = GitTools(repo_path)
                    self.gemini_client = GeminiClient()
                
                def run(self):
                    result = {
                        "has_changes": False,
                        "diff": "",
                        "commit_message": "",
                        "committed": False,
                        "pushed": False,
                        "error": ""
                    }
                    
                    try:
                        has_changes = self.git_tools.has_changes()
                        result["has_changes"] = has_changes
                        
                        if has_changes:
                            diff = self.git_tools.get_diff()
                            result["diff"] = diff
                            commit_message = self.gemini_client.generate_commit_message(diff)
                            result["commit_message"] = commit_message
                        
                        return result
                    except Exception as e:
                        result["error"] = str(e)
                        return result
            
            return FallbackAgent(repo_path)
    
    async def get_status(self):
        """Get current repository status"""
        try:
            repo_path = self.current_repo_path or self.repos_dir
            
            if not os.path.exists(repo_path):
                return {
                    "has_changes": False,
                    "current_branch": "unknown",
                    "repo_path": repo_path,
                    "timestamp": datetime.now().isoformat()
                }
            
            agent = self._get_agent(repo_path)
            has_changes = agent.git_tools.has_changes()
            branch = agent.git_tools.get_current_branch()
            
            return {
                "has_changes": has_changes,
                "current_branch": branch,
                "repo_path": repo_path,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error in get_status: {e}")
            return {
                "has_changes": False,
                "current_branch": "error",
                "repo_path": self.current_repo_path or self.repos_dir,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_repositories(self):
        """Get list of all repositories"""
        try:
            repos = self._load_repositories()
            
            for repo_id, repo_info in repos.items():
                repo_info["is_active"] = repo_info["path"] == self.current_repo_path
                
                if os.path.exists(repo_info["path"]):
                    repo_info["exists"] = True
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
                "active_repo_path": self.current_repo_path
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def clone_to_path(self, request, ws_manager):
        """Clone repository to specific path"""
        try:
            git_url = request.git_url.strip()
            clone_to_path = os.path.abspath(request.clone_to_path.strip())
            
            if not os.path.exists(os.path.dirname(clone_to_path)):
                raise HTTPException(status_code=400, detail=f"Parent directory does not exist")
            
            if os.path.exists(clone_to_path):
                raise HTTPException(status_code=400, detail=f"Path already exists")
            
            repo_name = request.name or git_url.split('/')[-1].replace('.git', '')
            repo_id = f"{repo_name}_{uuid.uuid4().hex[:8]}"
            
            await ws_manager.broadcast({
                "type": "clone_started",
                "message": f"Cloning repository to: {clone_to_path}"
            })
            
            result = subprocess.run(
                ["git", "clone", git_url, clone_to_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")
            
            repos = self._load_repositories()
            repos[repo_id] = {
                "id": repo_id,
                "name": repo_name,
                "git_url": git_url,
                "path": clone_to_path,
                "cloned_at": datetime.now().isoformat(),
                "is_active": False,
                "is_clone_to_path": True
            }
            self._save_repositories(repos)
            
            await ws_manager.broadcast({
                "type": "clone_complete",
                "message": f"Repository cloned successfully",
                "repo_id": repo_id
            })
            
            return {
                "success": True,
                "message": "Repository cloned successfully",
                "repo_id": repo_id,
                "repo_path": clone_to_path
            }
            
        except Exception as e:
            await ws_manager.broadcast({
                "type": "clone_error",
                "message": f"Clone failed: {str(e)}"
            })
            raise HTTPException(status_code=500, detail=str(e))
    
    async def clone_repository(self, request, ws_manager):
        """Clone repository to managed directory"""
        try:
            git_url = request.git_url.strip()
            repo_name = request.name or git_url.split('/')[-1].replace('.git', '')
            repo_id = f"{repo_name}_{uuid.uuid4().hex[:8]}"
            repo_path = os.path.join(self.repos_dir, repo_id)
            
            await ws_manager.broadcast({
                "type": "clone_started",
                "message": f"Cloning repository: {git_url}"
            })
            
            result = subprocess.run(
                ["git", "clone", git_url, repo_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")
            
            repos = self._load_repositories()
            repos[repo_id] = {
                "id": repo_id,
                "name": repo_name,
                "git_url": git_url,
                "path": repo_path,
                "cloned_at": datetime.now().isoformat(),
                "is_active": False
            }
            self._save_repositories(repos)
            
            await ws_manager.broadcast({
                "type": "clone_complete",
                "message": f"Repository cloned successfully",
                "repo_id": repo_id
            })
            
            return {
                "success": True,
                "message": "Repository cloned successfully",
                "repo_id": repo_id,
                "repo_path": repo_path
            }
            
        except Exception as e:
            await ws_manager.broadcast({
                "type": "clone_error",
                "message": f"Clone failed: {str(e)}"
            })
            raise HTTPException(status_code=500, detail=str(e))
    
    async def add_local_repository(self, request, ws_manager):
        """Add existing local repository"""
        try:
            local_path = os.path.abspath(request.local_path.strip())
            
            if not os.path.exists(local_path):
                raise HTTPException(status_code=400, detail="Path does not exist")
            
            if not os.path.isdir(local_path):
                raise HTTPException(status_code=400, detail="Path is not a directory")
            
            if not os.path.exists(os.path.join(local_path, '.git')):
                raise HTTPException(status_code=400, detail="Not a Git repository")
            
            await ws_manager.broadcast({
                "type": "local_add_started",
                "message": f"Adding local repository: {local_path}"
            })
            
            try:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=local_path,
                    capture_output=True,
                    text=True
                )
                git_url = result.stdout.strip() if result.returncode == 0 else "local-repository"
            except:
                git_url = "local-repository"
            
            repo_name = request.name or os.path.basename(local_path)
            repo_id = f"{repo_name}_{uuid.uuid4().hex[:8]}"
            
            repos = self._load_repositories()
            repos[repo_id] = {
                "id": repo_id,
                "name": repo_name,
                "git_url": git_url,
                "path": local_path,
                "cloned_at": datetime.now().isoformat(),
                "is_active": False,
                "is_local": True
            }
            self._save_repositories(repos)
            
            await ws_manager.broadcast({
                "type": "local_add_complete",
                "message": f"Local repository added successfully",
                "repo_id": repo_id
            })
            
            return {
                "success": True,
                "message": "Local repository added successfully",
                "repo_id": repo_id,
                "repo_path": local_path
            }
            
        except Exception as e:
            await ws_manager.broadcast({
                "type": "local_add_error",
                "message": f"Failed: {str(e)}"
            })
            raise HTTPException(status_code=500, detail=str(e))
    
    async def set_active_repository(self, request, ws_manager):
        """Set active repository"""
        try:
            repos = self._load_repositories()
            
            if request.repo_id not in repos:
                raise HTTPException(status_code=404, detail="Repository not found")
            
            repo_info = repos[request.repo_id]
            
            if not os.path.exists(repo_info["path"]):
                raise HTTPException(status_code=404, detail="Repository path does not exist")
            
            self.current_repo_path = repo_info["path"]
            
            for repo_id, repo_data in repos.items():
                repo_data["is_active"] = (repo_id == request.repo_id)
            self._save_repositories(repos)
            
            await ws_manager.broadcast({
                "type": "active_repo_changed",
                "message": f"Active repository changed to: {repo_info['name']}",
                "repo_id": request.repo_id,
                "repo_path": self.current_repo_path
            })
            
            return {
                "success": True,
                "message": "Active repository updated",
                "active_repo": repo_info
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def delete_repository(self, repo_id: str, ws_manager):
        """Delete repository"""
        try:
            repos = self._load_repositories()
            
            if repo_id not in repos:
                raise HTTPException(status_code=404, detail="Repository not found")
            
            repo_info = repos[repo_id]
            is_local = repo_info.get("is_local", False)
            was_active = repo_info["path"] == self.current_repo_path
            
            if was_active:
                self.current_repo_path = None
            
            if not is_local and os.path.exists(repo_info["path"]):
                try:
                    def handle_remove_readonly(func, path, exc):
                        os.chmod(path, stat.S_IWRITE)
                        func(path)
                    
                    shutil.rmtree(repo_info["path"], onerror=handle_remove_readonly)
                except Exception as e:
                    print(f"Error deleting files: {e}")
            
            del repos[repo_id]
            self._save_repositories(repos)
            
            await ws_manager.broadcast({
                "type": "repo_deleted",
                "message": f"Repository deleted",
                "repo_id": repo_id
            })
            
            return {
                "success": True,
                "message": "Repository deleted successfully"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def run_agent(self, ws_manager):
        """Run automation agent"""
        try:
            repo_path = self.current_repo_path or self.repos_dir
            
            if not os.path.exists(repo_path):
                raise HTTPException(status_code=400, detail="Repository path does not exist")
            
            agent = self._get_agent(repo_path)
            self.current_agent = agent
            
            await ws_manager.broadcast({
                "type": "workflow_started",
                "message": "Starting workflow..."
            })
            
            result = agent.run()
            self.current_workflow_state = result
            
            if result.get("commit_message") and not result.get("committed"):
                await ws_manager.broadcast({
                    "type": "approval_required",
                    "approval_type": "commit_approval",
                    "data": {
                        "type": "commit_approval",
                        "commit_message": result["commit_message"],
                        "security_summary": result.get("security_summary", ""),
                        "security_level": result.get("security_level", "safe"),
                        "instruction": "Please approve, reject, or edit the commit message"
                    }
                })
                
                return {
                    "success": True,
                    "message": "Workflow paused for approval",
                    "result": {"status": "awaiting_approval", "commit_message": result["commit_message"]}
                }
            else:
                await ws_manager.broadcast({
                    "type": "workflow_complete",
                    "message": "Workflow completed",
                    "result": result
                })
                
                return {
                    "success": True,
                    "message": "Workflow completed",
                    "result": result
                }
            
        except Exception as e:
            await ws_manager.broadcast({
                "type": "workflow_error",
                "message": str(e)
            })
            raise HTTPException(status_code=500, detail=str(e))
    
    async def handle_approval(self, request, ws_manager):
        """Handle approval responses"""
        try:
            if not self.current_agent or not self.current_workflow_state:
                raise HTTPException(status_code=400, detail="No active workflow")
            
            if request.approval_type == "commit":
                if request.action == "approve":
                    if request.commit_message:
                        self.current_workflow_state["commit_message"] = request.commit_message
                    
                    await ws_manager.broadcast({
                        "type": "step_update",
                        "message": "Committing changes..."
                    })
                    
                    if not self.current_agent.git_tools.git_add_all():
                        raise HTTPException(status_code=500, detail="Failed to stage changes")
                    
                    if self.current_agent.git_tools.git_commit(self.current_workflow_state["commit_message"]):
                        self.current_workflow_state["committed"] = True
                        
                        await ws_manager.broadcast({
                            "type": "step_complete",
                            "message": "Changes committed successfully!"
                        })
                        
                        await asyncio.sleep(1.5)
                        
                        await ws_manager.broadcast({
                            "type": "approval_required",
                            "approval_type": "push_approval",
                            "data": {
                                "type": "push_approval",
                                "commit_message": self.current_workflow_state["commit_message"],
                                "instruction": "Approve or reject push to remote"
                            }
                        })
                        
                        return {
                            "success": True,
                            "message": "Commit approved, awaiting push approval",
                            "result": {"status": "awaiting_push_approval"}
                        }
                    else:
                        raise HTTPException(status_code=500, detail="Failed to commit")
                
                elif request.action == "reject":
                    await ws_manager.broadcast({
                        "type": "workflow_complete",
                        "message": "Commit rejected"
                    })
                    
                    self.current_agent = None
                    self.current_workflow_state = None
                    
                    return {
                        "success": True,
                        "message": "Commit rejected",
                        "result": {"status": "rejected"}
                    }
            
            elif request.approval_type in ["push", "push_approval"]:
                if request.action == "approve":
                    await ws_manager.broadcast({
                        "type": "step_update",
                        "message": "Pushing to remote..."
                    })
                    
                    if self.current_agent.git_tools.git_push():
                        self.current_workflow_state["pushed"] = True
                        
                        await ws_manager.broadcast({
                            "type": "workflow_complete",
                            "message": "Changes pushed successfully!",
                            "result": self.current_workflow_state
                        })
                        
                        self.current_agent = None
                        self.current_workflow_state = None
                        
                        return {
                            "success": True,
                            "message": "Push completed",
                            "result": self.current_workflow_state
                        }
                    else:
                        raise HTTPException(status_code=500, detail="Failed to push")
                
                elif request.action == "reject":
                    await ws_manager.broadcast({
                        "type": "workflow_complete",
                        "message": "Push rejected. Changes remain local."
                    })
                    
                    self.current_agent = None
                    self.current_workflow_state = None
                    
                    return {
                        "success": True,
                        "message": "Push rejected",
                        "result": self.current_workflow_state
                    }
            
            return {
                "success": False,
                "message": f"Invalid approval state: {request.approval_type}"
            }
            
        except Exception as e:
            await ws_manager.broadcast({
                "type": "workflow_error",
                "message": str(e)
            })
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_workflow_status(self, thread_id: str):
        """Get workflow status"""
        try:
            repo_path = self.current_repo_path or self.repos_dir
            agent = self._get_agent(repo_path)
            
            state = agent.get_current_state(thread_id) if hasattr(agent, 'get_current_state') else None
            if not state:
                raise HTTPException(status_code=404, detail="Workflow not found")
            
            pending = agent.get_pending_approval(thread_id) if hasattr(agent, 'get_pending_approval') else None
            
            return {
                "thread_id": thread_id,
                "state": state,
                "pending_approval": pending,
                "is_paused": bool(pending)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
