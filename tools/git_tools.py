from git import Repo, GitCommandError
from typing import Optional, List, Tuple
import os
import sys

# Add parent directory to path to import security module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from security.security_scanner import SecurityScanner, SecurityLevel


class GitTools:
    def __init__(self, repo_path: str):
        try:
            self.repo = Repo(repo_path)
            # Initialize security scanner with GitGuardian API key if available
            gitguardian_key = os.getenv('GITGUARDIAN_API_KEY')
            self.security_scanner = SecurityScanner(gitguardian_api_key=gitguardian_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize Git repository at {repo_path}: {e}")
    
    def has_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        return self.repo.is_dirty(untracked_files=True)
    
    def get_diff(self) -> str:
        """Get the diff of all changes with enhanced context"""
        if not self.has_changes():
            return ""
        
        diff_parts = []
        
        # Get diff for staged changes
        staged_diff = self.repo.git.diff('--cached')
        if staged_diff:
            diff_parts.append("=== STAGED CHANGES ===")
            diff_parts.append(staged_diff)
        
        # Get diff for unstaged changes (modified files)
        unstaged_diff = self.repo.git.diff()
        if unstaged_diff:
            diff_parts.append("=== UNSTAGED CHANGES ===")
            diff_parts.append(unstaged_diff)
        
        # Get untracked files with their content (if they're small)
        untracked = self.repo.untracked_files
        if untracked:
            diff_parts.append("=== NEW FILES ===")
            for file in untracked:
                try:
                    file_path = self.repo.working_dir + "/" + file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Only include small files (< 1000 lines) to avoid overwhelming the AI
                        if len(content.splitlines()) < 1000:
                            diff_parts.append(f"New file: {file}")
                            diff_parts.append(content[:2000])  # Limit content size
                        else:
                            diff_parts.append(f"New file: {file} (large file, {len(content.splitlines())} lines)")
                except Exception as e:
                    diff_parts.append(f"New file: {file} (could not read: {e})")
        
        # Get summary of changed files
        try:
            changed_files = self.repo.git.diff('--name-only', 'HEAD').splitlines()
            if changed_files:
                diff_parts.append("=== CHANGED FILES ===")
                diff_parts.append("\n".join(changed_files))
        except:
            pass
        
        return "\n\n".join(diff_parts)
    
    def get_commit_diff(self) -> str:
        """Get a focused diff specifically for commit message generation"""
        if not self.has_changes():
            return ""
        
        diff_parts = []
        
        # Get summary of what changed
        try:
            # Get file stats
            stats = self.repo.git.diff('--stat')
            if stats:
                diff_parts.append("=== FILE CHANGES SUMMARY ===")
                diff_parts.append(stats)
        except:
            pass
        
        # Get actual diff but limit size
        try:
            diff = self.repo.git.diff()
            if diff:
                diff_parts.append("=== CODE CHANGES ===")
                # Limit diff size to avoid overwhelming the AI
                if len(diff) > 3000:
                    diff_parts.append(diff[:3000] + "\n... (diff truncated)")
                else:
                    diff_parts.append(diff)
        except:
            pass
        
        # List new files
        untracked = self.repo.untracked_files
        if untracked:
            diff_parts.append("=== NEW FILES ===")
            diff_parts.append("\n".join(untracked))
        
        return "\n\n".join(diff_parts)
    
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
    
    def get_security_analysis(self) -> Tuple[List, SecurityLevel, str]:
        """Get security analysis of current changes"""
        if not self.has_changes():
            return [], SecurityLevel.SAFE, "🛡️ No changes to analyze"
        
        # Get the diff content
        diff_content = self.get_commit_diff()
        
        # Get list of changed files
        changed_files = []
        try:
            # Get staged files
            staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
            changed_files.extend(staged_files)
            
            # Get unstaged files
            unstaged_files = [item.a_path for item in self.repo.index.diff(None)]
            changed_files.extend(unstaged_files)
            
            # Get untracked files
            changed_files.extend(self.repo.untracked_files)
            
            # Remove duplicates
            changed_files = list(set(changed_files))
        except:
            # Fallback to parsing diff for file names
            try:
                changed_files = self.repo.git.diff('--name-only', 'HEAD').splitlines()
            except:
                changed_files = []
        
        # Scan for security issues
        issues, overall_level = self.security_scanner.scan_diff(diff_content, changed_files)
        
        # Generate summary
        summary = self.security_scanner.get_security_summary(issues, overall_level)
        
        return issues, overall_level, summary
    
    def should_block_commit(self) -> Tuple[bool, str]:
        """Check if commit should be blocked due to security issues"""
        issues, overall_level, summary = self.get_security_analysis()
        
        should_block = self.security_scanner.should_block_commit(overall_level)
        
        if should_block:
            return True, f"🚫 COMMIT BLOCKED: Security issues detected\n\n{summary}"
        elif overall_level == SecurityLevel.CRITICAL:
            return False, f"⚠️ SECURITY WARNING: Please review carefully\n\n{summary}"
        elif overall_level == SecurityLevel.WARNING:
            return False, f"🔍 SECURITY NOTICE: Minor issues detected\n\n{summary}"
        else:
            return False, f"✅ SECURITY CHECK: Safe to commit\n\n{summary}"
