import re
import os
import requests
import asyncio
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class SecurityLevel(Enum):
    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"
    BLOCKED = "blocked"


@dataclass
class SecurityIssue:
    level: SecurityLevel
    type: str
    message: str
    file_path: str
    line_number: int = 0
    suggestion: str = ""


class SecurityScanner:
    def __init__(self, gitguardian_api_key: Optional[str] = None):
        # GitGuardian API configuration
        self.gitguardian_api_key = gitguardian_api_key or os.getenv('GITGUARDIAN_API_KEY')
        self.gitguardian_url = "https://api.gitguardian.com/v1/scan"
        
        # Define security patterns with their risk levels
        self.patterns = {
            # API Keys and Tokens
            'api_key': {
                'patterns': [
                    r'api[_-]?key\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
                    r'apikey\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
                    r'api[_-]?token\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
                ],
                'level': SecurityLevel.CRITICAL,
                'message': 'API key detected',
                'suggestion': 'Use environment variables or secure vault'
            },
            
            # Database Credentials
            'database_password': {
                'patterns': [
                    r'password\s*[=:]\s*["\']([^"\']{3,})["\']',
                    r'db[_-]?password\s*[=:]\s*["\']([^"\']{3,})["\']',
                    r'database[_-]?password\s*[=:]\s*["\']([^"\']{3,})["\']',
                ],
                'level': SecurityLevel.BLOCKED,
                'message': 'Database password detected',
                'suggestion': 'Use environment variables or encrypted config'
            },
            
            # Connection Strings
            'connection_string': {
                'patterns': [
                    r'mongodb://[^:]+:[^@]+@',
                    r'mysql://[^:]+:[^@]+@',
                    r'postgresql://[^:]+:[^@]+@',
                    r'redis://[^:]+:[^@]+@',
                ],
                'level': SecurityLevel.BLOCKED,
                'message': 'Database connection string with credentials',
                'suggestion': 'Use connection strings without embedded credentials'
            },
            
            # Private Keys
            'private_key': {
                'patterns': [
                    r'-----BEGIN PRIVATE KEY-----',
                    r'-----BEGIN RSA PRIVATE KEY-----',
                    r'-----BEGIN OPENSSH PRIVATE KEY-----',
                ],
                'level': SecurityLevel.BLOCKED,
                'message': 'Private key detected',
                'suggestion': 'Never commit private keys - use secure key management'
            },
            
            # JWT Secrets
            'jwt_secret': {
                'patterns': [
                    r'jwt[_-]?secret\s*[=:]\s*["\']([a-zA-Z0-9_-]{10,})["\']',
                    r'secret[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9_-]{10,})["\']',
                ],
                'level': SecurityLevel.CRITICAL,
                'message': 'JWT secret or secret key detected',
                'suggestion': 'Use environment variables for secrets'
            },
            
            # AWS Credentials
            'aws_credentials': {
                'patterns': [
                    r'AKIA[0-9A-Z]{16}',  # AWS Access Key ID
                    r'aws[_-]?access[_-]?key[_-]?id\s*[=:]\s*["\']?([A-Z0-9]{20})["\']?',
                    r'aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?',
                ],
                'level': SecurityLevel.BLOCKED,
                'message': 'AWS credentials detected',
                'suggestion': 'Use AWS IAM roles or environment variables'
            },
            
            # Generic Secrets
            'generic_secret': {
                'patterns': [
                    r'secret\s*[=:]\s*["\']([a-zA-Z0-9_-]{15,})["\']',
                    r'token\s*[=:]\s*["\']([a-zA-Z0-9_-]{20,})["\']',
                ],
                'level': SecurityLevel.WARNING,
                'message': 'Potential secret or token detected',
                'suggestion': 'Verify if this should be in environment variables'
            },
            
            # Email/Username in configs
            'email_in_config': {
                'patterns': [
                    r'email\s*[=:]\s*["\']([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})["\']',
                    r'username\s*[=:]\s*["\']([a-zA-Z0-9._-]{3,})["\']',
                ],
                'level': SecurityLevel.WARNING,
                'message': 'Email or username in configuration',
                'suggestion': 'Consider if this should be configurable'
            }
        }
        
        # Files that should never be committed
        self.sensitive_files = {
            '.env': SecurityLevel.CRITICAL,
            '.env.local': SecurityLevel.CRITICAL,
            '.env.production': SecurityLevel.BLOCKED,
            'id_rsa': SecurityLevel.BLOCKED,
            'id_dsa': SecurityLevel.BLOCKED,
            'id_ecdsa': SecurityLevel.BLOCKED,
            'id_ed25519': SecurityLevel.BLOCKED,
            '.aws/credentials': SecurityLevel.BLOCKED,
            '.ssh/id_rsa': SecurityLevel.BLOCKED,
            'database.yml': SecurityLevel.WARNING,
            'config/database.yml': SecurityLevel.WARNING,
        }
        
        # Sensitive file patterns that should be in .gitignore
        self.sensitive_patterns = {
            '.env': 'Environment files with secrets',
            '*.key': 'Private key files',
            '*.pem': 'Certificate files',
            '*.p12': 'Certificate files',
            '*.pfx': 'Certificate files',
            'id_rsa': 'SSH private keys',
            'id_dsa': 'SSH private keys',
            'id_ecdsa': 'SSH private keys',
            'id_ed25519': 'SSH private keys',
            '.aws/credentials': 'AWS credential files',
            'config/database.yml': 'Database configuration',
            'secrets.json': 'Secret configuration files',
            '.secret': 'Secret files',
        }
        
        # File extensions that are more likely to contain secrets
        self.risky_extensions = {
            '.env', '.config', '.conf', '.ini', '.yaml', '.yml', 
            '.json', '.xml', '.properties', '.cfg', '.toml'
        }

    def scan_diff(self, diff_content: str, file_paths: List[str] = None) -> Tuple[List[SecurityIssue], SecurityLevel]:
        """Scan git diff for security issues using both custom and GitGuardian scanning"""
        issues = []
        max_level = SecurityLevel.SAFE
        
        # Phase 1: Custom Scanner (Always runs - fast and unique features)
        print("🛡️ Running custom security analysis...")
        
        # Scan file paths for sensitive files
        if file_paths:
            for file_path in file_paths:
                file_issues = self._scan_file_path(file_path)
                issues.extend(file_issues)
                for issue in file_issues:
                    if self._is_higher_level(issue.level, max_level):
                        max_level = issue.level
        
        # Enhanced: Check for .gitignore modifications
        gitignore_issues = self._scan_gitignore_changes(diff_content, file_paths or [])
        issues.extend(gitignore_issues)
        for issue in gitignore_issues:
            if self._is_higher_level(issue.level, max_level):
                max_level = issue.level
        
        # Enhanced: Check for newly tracked sensitive files
        tracking_issues = self._scan_newly_tracked_files(file_paths or [])
        issues.extend(tracking_issues)
        for issue in tracking_issues:
            if self._is_higher_level(issue.level, max_level):
                max_level = issue.level
        
        # Scan diff content for patterns
        content_issues = self._scan_content(diff_content, file_paths or [])
        issues.extend(content_issues)
        for issue in content_issues:
            if self._is_higher_level(issue.level, max_level):
                max_level = issue.level
        
        # Phase 2: GitGuardian API (If available - comprehensive detection)
        if self.gitguardian_api_key:
            print("🌐 Running GitGuardian API analysis...")
            try:
                gitguardian_issues = self._scan_with_gitguardian(diff_content, file_paths or [])
                issues.extend(gitguardian_issues)
                for issue in gitguardian_issues:
                    if self._is_higher_level(issue.level, max_level):
                        max_level = issue.level
            except Exception as e:
                print(f"⚠️ GitGuardian API error (falling back to custom only): {e}")
                # Add a warning but don't fail
                issues.append(SecurityIssue(
                    level=SecurityLevel.WARNING,
                    type='api_fallback',
                    message='GitGuardian API unavailable, using custom scanner only',
                    file_path='system',
                    suggestion='Check GitGuardian API key and network connection'
                ))
        else:
            print("ℹ️ GitGuardian API key not provided, using custom scanner only")
        
        return issues, max_level

    def _scan_file_path(self, file_path: str) -> List[SecurityIssue]:
        """Check if file path contains sensitive files"""
        issues = []
        
        # Check exact file matches
        for sensitive_file, level in self.sensitive_files.items():
            if file_path.endswith(sensitive_file):
                issues.append(SecurityIssue(
                    level=level,
                    type='sensitive_file',
                    message=f'Sensitive file detected: {sensitive_file}',
                    file_path=file_path,
                    suggestion='Add to .gitignore or use environment variables'
                ))
        
        return issues

    def _scan_content(self, content: str, file_paths: List[str]) -> List[SecurityIssue]:
        """Scan content for security patterns"""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip lines that are deletions (start with -)
            if line.startswith('-'):
                continue
                
            # Focus on additions (start with +) or context lines
            line_content = line[1:] if line.startswith(('+', '-', ' ')) else line
            
            # Scan each pattern
            for pattern_name, pattern_info in self.patterns.items():
                for pattern in pattern_info['patterns']:
                    matches = re.finditer(pattern, line_content, re.IGNORECASE)
                    for match in matches:
                        # Determine which file this line belongs to
                        file_path = self._get_file_for_line(line_num, content, file_paths)
                        
                        issues.append(SecurityIssue(
                            level=pattern_info['level'],
                            type=pattern_name,
                            message=pattern_info['message'],
                            file_path=file_path,
                            line_number=line_num,
                            suggestion=pattern_info['suggestion']
                        ))
        
        return issues

    def _get_file_for_line(self, line_num: int, content: str, file_paths: List[str]) -> str:
        """Try to determine which file a line belongs to from diff context"""
        lines = content.split('\n')
        current_file = "unknown"
        
        for i, line in enumerate(lines[:line_num]):
            if line.startswith('+++') or line.startswith('---'):
                # Extract file path from diff header
                parts = line.split('\t')[0].split(' ')
                if len(parts) > 1:
                    current_file = parts[1].lstrip('b/')
        
        return current_file

    def _is_higher_level(self, level1: SecurityLevel, level2: SecurityLevel) -> bool:
        """Check if level1 is higher priority than level2"""
        priority = {
            SecurityLevel.SAFE: 0,
            SecurityLevel.WARNING: 1,
            SecurityLevel.CRITICAL: 2,
            SecurityLevel.BLOCKED: 3
        }
        return priority[level1] > priority[level2]

    def get_security_summary(self, issues: List[SecurityIssue], overall_level: SecurityLevel) -> str:
        """Generate a human-readable security summary"""
        if not issues:
            return "🛡️ SECURITY: No sensitive data detected - Safe to commit"
        
        summary_parts = []
        
        # Group issues by level and type
        blocked = [i for i in issues if i.level == SecurityLevel.BLOCKED]
        critical = [i for i in issues if i.level == SecurityLevel.CRITICAL]
        warnings = [i for i in issues if i.level == SecurityLevel.WARNING]
        
        # Special handling for different issue types
        gitignore_issues = [i for i in issues if i.type == 'gitignore_removal']
        tracking_issues = [i for i in issues if i.type in ['newly_tracked_sensitive_file', 'potentially_sensitive_file']]
        gitguardian_issues = [i for i in issues if i.type == 'gitguardian_detection']
        api_issues = [i for i in issues if i.type.startswith('api_')]
        
        if blocked:
            summary_parts.append(f"🚫 BLOCKED: {len(blocked)} critical security issue(s)")
            for issue in blocked[:2]:  # Show first 2
                summary_parts.append(f"   • {issue.message}")
        
        if critical:
            summary_parts.append(f"⚠️ CRITICAL: {len(critical)} security issue(s)")
            for issue in critical[:2]:  # Show first 2
                summary_parts.append(f"   • {issue.message}")
        
        if gitignore_issues:
            summary_parts.append(f"🔒 GITIGNORE: {len(gitignore_issues)} protection(s) removed")
            for issue in gitignore_issues[:2]:
                summary_parts.append(f"   • {issue.message}")
        
        if tracking_issues:
            summary_parts.append(f"📁 FILE TRACKING: {len(tracking_issues)} sensitive file(s) detected")
            for issue in tracking_issues[:2]:
                summary_parts.append(f"   • {issue.message}")
        
        if gitguardian_issues:
            summary_parts.append(f"🌐 GITGUARDIAN: {len(gitguardian_issues)} advanced detection(s)")
            for issue in gitguardian_issues[:2]:
                summary_parts.append(f"   • {issue.message}")
        
        if api_issues:
            summary_parts.append(f"🔧 API STATUS: {len(api_issues)} service issue(s)")
            for issue in api_issues[:1]:
                summary_parts.append(f"   • {issue.message}")
        
        if warnings and not (gitignore_issues or tracking_issues or gitguardian_issues or api_issues):
            summary_parts.append(f"🔍 WARNING: {len(warnings)} potential issue(s)")
        
        # Add scanning method info
        has_gitguardian = any(i.type == 'gitguardian_detection' for i in issues)
        has_custom = any(i.type not in ['gitguardian_detection', 'api_auth_error', 'api_rate_limit', 'api_timeout', 'api_fallback'] for i in issues)
        
        scan_methods = []
        if has_custom:
            scan_methods.append("Custom Scanner")
        if has_gitguardian:
            scan_methods.append("GitGuardian API")
        
        if scan_methods:
            summary_parts.append(f"\n🔍 Scanned with: {' + '.join(scan_methods)}")
        
        # Add overall recommendation
        if overall_level == SecurityLevel.BLOCKED:
            summary_parts.append("\n❌ RECOMMENDATION: DO NOT COMMIT - Fix security issues first")
        elif overall_level == SecurityLevel.CRITICAL:
            summary_parts.append("\n⚠️ RECOMMENDATION: Review carefully before committing")
            if gitignore_issues:
                summary_parts.append("   Consider the long-term impact of .gitignore changes")
        elif overall_level == SecurityLevel.WARNING:
            summary_parts.append("\n🔍 RECOMMENDATION: Consider if these values should be configurable")
        else:
            summary_parts.append("\n✅ RECOMMENDATION: Safe to commit")
        
        return "\n".join(summary_parts)

    def should_block_commit(self, overall_level: SecurityLevel) -> bool:
        """Determine if commit should be blocked based on security level"""
        return overall_level == SecurityLevel.BLOCKED

    def _scan_gitignore_changes(self, diff_content: str, file_paths: List[str]) -> List[SecurityIssue]:
        """Enhanced: Scan for dangerous .gitignore modifications"""
        issues = []
        
        # Check if .gitignore is being modified
        if not any('.gitignore' in path for path in file_paths):
            return issues
        
        # Parse diff to find removed lines (lines starting with -)
        lines = diff_content.split('\n')
        in_gitignore_section = False
        
        for line in lines:
            # Detect .gitignore file section in diff
            if '--- a/.gitignore' in line or '+++ b/.gitignore' in line:
                in_gitignore_section = True
                continue
            elif line.startswith('--- ') or line.startswith('+++ '):
                in_gitignore_section = False
                continue
            
            # Check for removed lines in .gitignore
            if in_gitignore_section and line.startswith('-') and not line.startswith('---'):
                removed_pattern = line[1:].strip()
                
                # Check if removed pattern matches sensitive files
                for pattern, description in self.sensitive_patterns.items():
                    if pattern in removed_pattern or removed_pattern in pattern:
                        issues.append(SecurityIssue(
                            level=SecurityLevel.CRITICAL,
                            type='gitignore_removal',
                            message=f'Sensitive pattern "{removed_pattern}" removed from .gitignore',
                            file_path='.gitignore',
                            suggestion=f'Keep "{removed_pattern}" in .gitignore to protect {description.lower()}'
                        ))
        
        return issues

    def _scan_newly_tracked_files(self, file_paths: List[str]) -> List[SecurityIssue]:
        """Enhanced: Check for newly tracked sensitive files"""
        issues = []
        
        for file_path in file_paths:
            # Check if this is a sensitive file being tracked for the first time
            file_name = file_path.split('/')[-1]
            
            # Direct sensitive file matches
            for sensitive_file, level in self.sensitive_files.items():
                if file_path.endswith(sensitive_file) or file_name == sensitive_file:
                    issues.append(SecurityIssue(
                        level=level,
                        type='newly_tracked_sensitive_file',
                        message=f'Sensitive file "{file_path}" is being tracked',
                        file_path=file_path,
                        suggestion=f'Add "{file_path}" to .gitignore and use environment variables instead'
                    ))
            
            # Pattern-based matches
            for pattern in self.sensitive_patterns.keys():
                if self._matches_pattern(file_path, pattern):
                    issues.append(SecurityIssue(
                        level=SecurityLevel.WARNING,
                        type='potentially_sensitive_file',
                        message=f'File "{file_path}" matches sensitive pattern "{pattern}"',
                        file_path=file_path,
                        suggestion=f'Verify "{file_path}" contains no secrets, or add to .gitignore'
                    ))
        
        return issues

    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches a gitignore-style pattern"""
        import fnmatch
        
        # Handle different pattern types
        if '*' in pattern:
            return fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(file_path.split('/')[-1], pattern)
        else:
            return pattern in file_path or file_path.endswith(pattern)

    def _scan_with_gitguardian(self, diff_content: str, file_paths: List[str]) -> List[SecurityIssue]:
        """Scan using GitGuardian API for comprehensive secret detection"""
        issues = []
        
        if not self.gitguardian_api_key:
            return issues
        
        try:
            # Prepare the request payload
            headers = {
                'Authorization': f'Token {self.gitguardian_api_key}',
                'Content-Type': 'application/json'
            }
            
            # Create documents for GitGuardian API
            documents = []
            
            # Add diff content as a document
            if diff_content.strip():
                documents.append({
                    'filename': 'git.diff',
                    'document': diff_content
                })
            
            # If no documents to scan, return empty
            if not documents:
                return issues
            
            payload = {
                'documents': documents
            }
            
            # Make API request
            response = requests.post(
                self.gitguardian_url,
                json=payload,
                headers=headers,
                timeout=10  # 10 second timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Process GitGuardian results
                for doc_result in result.get('scan_results', []):
                    for policy_break in doc_result.get('policy_breaks', []):
                        # Map GitGuardian severity to our levels
                        severity = policy_break.get('break_type', 'unknown')
                        if severity in ['secret', 'high']:
                            level = SecurityLevel.BLOCKED
                        elif severity in ['medium', 'potential_secret']:
                            level = SecurityLevel.CRITICAL
                        else:
                            level = SecurityLevel.WARNING
                        
                        # Extract information
                        secret_type = policy_break.get('policy', 'Unknown Secret Type')
                        validity = policy_break.get('validity', 'unknown')
                        
                        # Create issue
                        message = f"GitGuardian: {secret_type} detected"
                        if validity == 'valid':
                            message += " (VALID - Active secret!)"
                            level = SecurityLevel.BLOCKED
                        elif validity == 'invalid':
                            message += " (Invalid format)"
                            level = SecurityLevel.WARNING
                        
                        suggestion = f"Remove {secret_type.lower()} and use secure storage"
                        if validity == 'valid':
                            suggestion += ". URGENT: This is an active secret that should be rotated immediately!"
                        
                        issues.append(SecurityIssue(
                            level=level,
                            type='gitguardian_detection',
                            message=message,
                            file_path=doc_result.get('filename', 'unknown'),
                            suggestion=suggestion
                        ))
            
            elif response.status_code == 401:
                issues.append(SecurityIssue(
                    level=SecurityLevel.WARNING,
                    type='api_auth_error',
                    message='GitGuardian API authentication failed',
                    file_path='system',
                    suggestion='Check your GitGuardian API key'
                ))
            
            elif response.status_code == 429:
                issues.append(SecurityIssue(
                    level=SecurityLevel.WARNING,
                    type='api_rate_limit',
                    message='GitGuardian API rate limit exceeded',
                    file_path='system',
                    suggestion='Wait before making more requests or upgrade your GitGuardian plan'
                ))
            
            else:
                print(f"GitGuardian API returned status {response.status_code}: {response.text}")
        
        except requests.exceptions.Timeout:
            issues.append(SecurityIssue(
                level=SecurityLevel.WARNING,
                type='api_timeout',
                message='GitGuardian API request timed out',
                file_path='system',
                suggestion='Check network connection or try again later'
            ))
        
        except requests.exceptions.RequestException as e:
            print(f"GitGuardian API request failed: {e}")
        
        except Exception as e:
            print(f"Unexpected error with GitGuardian API: {e}")
        
        return issues