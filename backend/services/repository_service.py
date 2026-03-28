"""
Repository Service
Handles all repository management operations including cloning, tracking, and deletion
"""

import os
import json
import uuid
import subprocess
import shutil
import stat
from datetime import datetime
from typing import Dict, Tuple, Optional
from pathlib import Path


class RepositoryService:
    """
    Service for managing Git repositories (clone, add, delete, track)
    
    Handles repository configuration persistence and filesystem operations
    """
    
    def __init__(self, repos_dir: str, config_file: str):
        """
        Initialize repository service with storage locations
        
        Args:
            repos_dir: Directory where cloned repositories are stored
            config_file: Path to JSON file storing repository configuration
        """
        self.repos_dir = repos_dir
        self.config_file = config_file
        
        # Ensure repositories directory exists
        os.makedirs(repos_dir, exist_ok=True)
    
    def load_repositories(self) -> Dict:
        """
        Load repository configuration from JSON file
        
        Returns:
            Dictionary mapping repository IDs to their configuration
            
        Note:
            Returns empty dict if config file doesn't exist or is invalid
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_repositories(self, repos: Dict):
        """
        Persist repository configuration to JSON file
        
        Args:
            repos: Dictionary of repository configurations to save
        """
        with open(self.config_file, 'w') as f:
            json.dump(repos, f, indent=2)
    
    async def clone_to_path(self, git_url: str, clone_to_path: str, name: Optional[str] = None) -> Tuple[bool, str, Dict]:
        """
        Clone a Git repository to a specific local path
        
        Args:
            git_url: URL of Git repository to clone
            clone_to_path: Local filesystem path for cloning
            name: Optional custom name for repository
            
        Returns:
            Tuple of (success, message, result_data)
            
        Raises:
            Exception: If clone operation fails or path validation fails
        """
        # Normalize and validate path
        clone_to_path = os.path.abspath(clone_to_path)
        parent_dir = os.path.dirname(clone_to_path)
        
        if not os.path.exists(parent_dir):
            return False, f"Parent directory does not exist: {parent_dir}", {}
        
        # Check if target path already exists
        if os.path.exists(clone_to_path):
            try:
                items = os.listdir(clone_to_path)
                visible_items = [item for item in items if not item.startswith('.')]
                
                if visible_items:
                    return False, f"Directory is not empty: {clone_to_path}", {}
                else:
                    print(f"📁 Directory exists but is empty, proceeding: {clone_to_path}")
            except OSError:
                return False, f"Cannot access directory: {clone_to_path}", {}
        else:
            try:
                os.makedirs(clone_to_path, exist_ok=True)
                print(f"📁 Created directory: {clone_to_path}")
            except OSError as e:
                return False, f"Cannot create directory: {clone_to_path}. Error: {str(e)}", {}
        
        # Extract repository name
        repo_name = name or git_url.split('/')[-1].replace('.git', '')
        repo_id = f"{repo_name}_{uuid.uuid4().hex[:8]}"
        
        # Execute git clone
        try:
            result = subprocess.run(
                ["git", "clone", git_url, "."],
                cwd=clone_to_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                # Clean up on failure
                if os.path.exists(clone_to_path):
                    shutil.rmtree(clone_to_path, ignore_errors=True)
                return False, f"Git clone failed: {result.stderr}", {}
            
            # Save repository configuration
            repos = self.load_repositories()
            repos[repo_id] = {
                "id": repo_id,
                "name": repo_name,
                "git_url": git_url,
                "path": clone_to_path,
                "cloned_at": datetime.now().isoformat(),
                "is_active": False,
                "is_clone_to_path": True
            }
            self.save_repositories(repos)
            
            return True, "Repository cloned successfully", {
                "repo_id": repo_id,
                "repo_path": clone_to_path
            }
            
        except subprocess.TimeoutExpired:
            if os.path.exists(clone_to_path):
                shutil.rmtree(clone_to_path, ignore_errors=True)
            return False, "Clone operation timed out", {}
        except Exception as e:
            if os.path.exists(clone_to_path):
                shutil.rmtree(clone_to_path, ignore_errors=True)
            return False, f"Clone failed: {str(e)}", {}
    
    async def add_local_repository(self, local_path: str, name: Optional[str] = None) -> Tuple[bool, str, Dict]:
        """
        Add an existing local Git repository to management
        
        Args:
            local_path: Path to existing Git repository
            name: Optional custom name for repository
            
        Returns:
            Tuple of (success, message, result_data)
            
        Validates:
            - Path exists and is a directory
            - Directory contains .git folder (is a Git repository)
        """
        local_path = os.path.abspath(local_path)
        
        # Validate path exists
        if not os.path.exists(local_path):
            return False, f"Path does not exist: {local_path}", {}
        
        # Validate is directory
        if not os.path.isdir(local_path):
            return False, f"Path is not a directory: {local_path}", {}
        
        # Validate is Git repository
        git_dir = os.path.join(local_path, '.git')
        if not os.path.exists(git_dir):
            return False, f"Not a Git repository (no .git folder found): {local_path}", {}
        
        try:
            # Get remote URL if available
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
            
            # Extract repository name
            repo_name = name or os.path.basename(local_path)
            repo_id = f"{repo_name}_{uuid.uuid4().hex[:8]}"
            
            # Save repository configuration
            repos = self.load_repositories()
            repos[repo_id] = {
                "id": repo_id,
                "name": repo_name,
                "git_url": git_url,
                "path": local_path,
                "cloned_at": datetime.now().isoformat(),
                "is_active": False,
                "is_local": True
            }
            self.save_repositories(repos)
            
            return True, "Local repository added successfully", {
                "repo_id": repo_id,
                "repo_path": local_path
            }
            
        except Exception as e:
            return False, f"Failed to analyze repository: {str(e)}", {}
    
    async def delete_repository(self, repo_id: str, current_repo_path: str, default_repo_path: str) -> Tuple[bool, str, bool]:
        """
        Delete a repository and optionally remove its files
        
        Args:
            repo_id: Unique identifier of repository to delete
            current_repo_path: Path of currently active repository
            default_repo_path: Default repository path to fall back to
            
        Returns:
            Tuple of (success, message, was_active)
            
        Behavior:
            - Local repositories: Only removed from tracking, files preserved
            - Cloned repositories: Files permanently deleted from filesystem
            - Active repository: Automatically resets to default
        """
        repos = self.load_repositories()
        
        if repo_id not in repos:
            return False, "Repository not found", False
        
        repo_info = repos[repo_id]
        is_local = repo_info.get("is_local", False)
        is_clone_to_path = repo_info.get("is_clone_to_path", False)
        
        # Check if this is the active repository
        was_active = repo_info["path"] == current_repo_path
        if was_active:
            print(f"⚠️ Deleted active repository, will reset to default: {default_repo_path}")
        
        # Handle deletion based on repository type
        if is_local:
            # Local repositories: only remove from tracking
            print(f"📁 Removing local repository from list (keeping files): {repo_info['path']}")
        elif is_clone_to_path or True:  # Delete cloned repositories
            repo_path = repo_info["path"]
            print(f"🗑️ Attempting to delete repository folder: {repo_path}")
            
            if os.path.exists(repo_path):
                try:
                    # Calculate folder size for logging
                    total_size = 0
                    for dirpath, dirnames, filenames in os.walk(repo_path):
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            try:
                                total_size += os.path.getsize(filepath)
                            except:
                                pass
                    
                    size_mb = total_size / (1024 * 1024)
                    print(f"📁 Folder size: {size_mb:.2f} MB")
                    
                    # Force remove all files and subdirectories
                    shutil.rmtree(repo_path, ignore_errors=False)
                    print(f"✅ Successfully deleted repository folder: {repo_path}")
                    
                    # Verify deletion
                    if os.path.exists(repo_path):
                        print(f"⚠️ Warning: Folder still exists after deletion attempt")
                        shutil.rmtree(repo_path, ignore_errors=True)
                        if os.path.exists(repo_path):
                            return False, f"Failed to completely remove folder: {repo_path}", was_active
                    else:
                        print(f"✅ Confirmed: Folder completely removed from disk")
                        
                except PermissionError as e:
                    print(f"⚠️ Permission error deleting files: {e}")
                    print(f"🔧 Trying alternative deletion method...")
                    
                    # Try to change permissions and delete again
                    try:
                        def handle_remove_readonly(func, path, exc):
                            os.chmod(path, stat.S_IWRITE)
                            func(path)
                        
                        shutil.rmtree(repo_path, onerror=handle_remove_readonly)
                        print(f"✅ Successfully deleted with permission fix: {repo_path}")
                    except Exception as e2:
                        print(f"❌ Still failed after permission fix: {e2}")
                        return False, f"Failed to delete repository files due to permissions: {str(e)}", was_active
                        
                except Exception as e:
                    print(f"❌ Error deleting repository files: {e}")
                    return False, f"Failed to delete repository files: {str(e)}", was_active
            else:
                print(f"⚠️ Repository folder does not exist: {repo_path}")
                print(f"📍 Expected location: {os.path.abspath(repo_path)}")
        
        # Remove from configuration
        del repos[repo_id]
        self.save_repositories(repos)
        
        action_word = "removed from list" if is_local else "completely removed from system"
        print(f"✅ Repository '{repo_info['name']}' {action_word}")
        
        message = f"Repository '{repo_info['name']}' {'removed from list' if is_local else 'and all its files have been deleted successfully'}"
        return True, message, was_active