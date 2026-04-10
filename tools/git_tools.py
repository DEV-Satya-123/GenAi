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

    def search_commits(self, query: str, max_results: int = 10) -> List[dict]:
        """
        Search commits by message, author, or content
        
        Args:
            query: Search term
            max_results: Maximum number of results to return
            
        Returns:
            List of commit dictionaries with hash, message, author, date
        """
        try:
            results = []
            # Search in commit messages
            commits = list(self.repo.iter_commits(max_count=100))
            
            for commit in commits:
                # Search in commit message
                if query.lower() in commit.message.lower():
                    results.append({
                        'hash': commit.hexsha[:7],
                        'full_hash': commit.hexsha,
                        'message': commit.message.strip(),
                        'author': str(commit.author),
                        'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        'files_changed': len(commit.stats.files)
                    })
                    
                    if len(results) >= max_results:
                        break
            
            return results
        except Exception as e:
            print(f"Error searching commits: {e}")
            return []
    
    def get_commit_history(self, max_count: int = 20) -> List[dict]:
        """Get recent commit history"""
        try:
            commits = []
            for commit in self.repo.iter_commits(max_count=max_count):
                commits.append({
                    'hash': commit.hexsha[:7],
                    'full_hash': commit.hexsha,
                    'message': commit.message.strip(),
                    'author': str(commit.author),
                    'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'files_changed': len(commit.stats.files)
                })
            return commits
        except Exception as e:
            print(f"Error getting commit history: {e}")
            return []
    
    def check_gitignore_exists(self) -> bool:
        """Check if .gitignore file exists"""
        gitignore_path = os.path.join(self.repo.working_dir, '.gitignore')
        return os.path.exists(gitignore_path)
    
    def create_gitignore(self, template: str = 'python') -> bool:
        """
        Create a .gitignore file with common patterns
        
        Args:
            template: Type of project (python, node, java, etc.)
        """
        gitignore_path = os.path.join(self.repo.working_dir, '.gitignore')
        
        templates = {
            'python': """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/

# Environment
.env
.env.local
*.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Secrets
secrets/
*.key
*.pem
credentials.json
""",
            'node': """# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# Environment
.env
.env.local
.env.*.local

# Build
dist/
build/
.next/
out/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
""",
            'general': """# Environment
.env
.env.local
*.env

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Secrets
secrets/
*.key
*.pem
credentials.json
"""
        }
        
        try:
            content = templates.get(template, templates['general'])
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created .gitignore with {template} template")
            return True
        except Exception as e:
            print(f"❌ Error creating .gitignore: {e}")
            return False
    
    def get_sensitive_files_not_ignored(self) -> List[str]:
        """
        Detect sensitive files that should be in .gitignore but aren't
        
        Returns:
            List of file patterns that should be added to .gitignore
        """
        sensitive_patterns = [
            '.env', '.env.local', '.env.production', '.env.development',
            'secrets/', 'credentials.json', '*.key', '*.pem',
            'config/secrets.yml', 'config/database.yml',
            '*.log', 'logs/', 'npm-debug.log',
            '__pycache__/', '*.pyc', 'venv/', 'env/',
            'node_modules/', '.DS_Store', 'Thumbs.db',
            '*.db', '*.sqlite', '*.sqlite3',
            'id_rsa', 'id_rsa.pub', '*.ppk'
        ]
        
        missing_patterns = []
        gitignore_path = os.path.join(self.repo.working_dir, '.gitignore')
        
        # Read existing .gitignore
        existing_patterns = set()
        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            existing_patterns.add(line)
            except Exception as e:
                print(f"Warning: Could not read .gitignore: {e}")
        
        # Check which sensitive patterns are missing
        for pattern in sensitive_patterns:
            if pattern not in existing_patterns:
                # Check if any files matching this pattern exist
                if self._pattern_matches_files(pattern):
                    missing_patterns.append(pattern)
        
        return missing_patterns
    
    def _pattern_matches_files(self, pattern: str) -> bool:
        """Check if a pattern matches any files in the repository"""
        try:
            import fnmatch
            
            # Handle directory patterns
            if pattern.endswith('/'):
                dir_name = pattern.rstrip('/')
                for root, dirs, files in os.walk(self.repo.working_dir):
                    if dir_name in dirs:
                        return True
            
            # Handle file patterns
            for root, dirs, files in os.walk(self.repo.working_dir):
                # Skip .git directory
                if '.git' in root:
                    continue
                    
                for file in files:
                    if fnmatch.fnmatch(file, pattern) or fnmatch.fnmatch(os.path.join(root, file), pattern):
                        return True
            
            return False
        except Exception:
            return False
    
    def add_to_gitignore(self, patterns: List[str]) -> bool:
        """
        Add patterns to .gitignore file
        
        Args:
            patterns: List of patterns to add
        """
        gitignore_path = os.path.join(self.repo.working_dir, '.gitignore')
        
        try:
            # Read existing content
            existing_content = ""
            if os.path.exists(gitignore_path):
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # Add new patterns
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                if existing_content and not existing_content.endswith('\n'):
                    f.write('\n')
                
                f.write('\n# Auto-added sensitive file patterns\n')
                for pattern in patterns:
                    f.write(f'{pattern}\n')
            
            print(f"✅ Added {len(patterns)} patterns to .gitignore")
            return True
        except Exception as e:
            print(f"❌ Error updating .gitignore: {e}")
            return False
    
    def smart_gitignore_check(self) -> dict:
        """
        Smart .gitignore management:
        1. Check if .gitignore exists
        2. If not, suggest creating one
        3. If yes, check for missing sensitive patterns
        
        Returns:
            Dictionary with status and recommendations
        """
        result = {
            'has_gitignore': False,
            'missing_patterns': [],
            'recommendations': [],
            'auto_fix_available': False
        }
        
        # Check if .gitignore exists
        result['has_gitignore'] = self.check_gitignore_exists()
        
        if not result['has_gitignore']:
            result['recommendations'].append('Create .gitignore file')
            result['auto_fix_available'] = True
            return result
        
        # Check for missing sensitive patterns
        missing = self.get_sensitive_files_not_ignored()
        result['missing_patterns'] = missing
        
        if missing:
            result['recommendations'].append(f'Add {len(missing)} sensitive patterns to .gitignore')
            result['auto_fix_available'] = True
        else:
            result['recommendations'].append('✅ .gitignore is properly configured')
        
        return result
    
    def auto_fix_gitignore(self, project_type: str = 'python') -> dict:
        """
        Automatically fix .gitignore issues
        
        Args:
            project_type: Type of project for template selection
            
        Returns:
            Dictionary with actions taken
        """
        result = {
            'actions_taken': [],
            'success': True,
            'message': ''
        }
        
        # Check if .gitignore exists
        if not self.check_gitignore_exists():
            if self.create_gitignore(project_type):
                result['actions_taken'].append(f'Created .gitignore with {project_type} template')
            else:
                result['success'] = False
                result['message'] = 'Failed to create .gitignore'
                return result
        
        # Check for missing patterns
        missing = self.get_sensitive_files_not_ignored()
        if missing:
            if self.add_to_gitignore(missing):
                result['actions_taken'].append(f'Added {len(missing)} sensitive patterns to .gitignore')
            else:
                result['success'] = False
                result['message'] = 'Failed to update .gitignore'
                return result
        
        if not result['actions_taken']:
            result['message'] = '✅ .gitignore is already properly configured'
        else:
            result['message'] = f"✅ Fixed .gitignore: {', '.join(result['actions_taken'])}"
        
        return result
