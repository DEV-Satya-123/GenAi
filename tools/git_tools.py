from git import Repo, GitCommandError
from typing import Optional


class GitTools:
    def __init__(self, repo_path: str):
        try:
            self.repo = Repo(repo_path)
        except Exception as e:
            raise ValueError(f"Failed to initialize Git repository at {repo_path}: {e}")
    
    def has_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        return self.repo.is_dirty(untracked_files=True)
    
    def get_diff(self) -> str:
        """Get the diff of all changes"""
        if not self.has_changes():
            return ""
        
        # Get diff for tracked files
        diff = self.repo.git.diff()
        
        # Get untracked files
        untracked = self.repo.untracked_files
        if untracked:
            diff += f"\n\nUntracked files:\n" + "\n".join(untracked)
        
        return diff
    
    def git_add_all(self) -> bool:
        """Stage all changes"""
        try:
            self.repo.git.add(A=True)
            return True
        except GitCommandError as e:
            print(f"Error adding files: {e}")
            return False
    
    def git_commit(self, message: str) -> bool:
        """Commit staged changes"""
        try:
            self.repo.index.commit(message)
            return True
        except GitCommandError as e:
            print(f"Error committing: {e}")
            return False
    
    def git_push(self, remote: str = "origin", branch: Optional[str] = None) -> bool:
        """Push commits to remote"""
        try:
            if branch is None:
                branch = self.repo.active_branch.name
            
            origin = self.repo.remote(name=remote)
            origin.push(branch)
            return True
        except GitCommandError as e:
            print(f"Error pushing: {e}")
            return False
    
    def get_current_branch(self) -> str:
        """Get the current branch name"""
        return self.repo.active_branch.name
