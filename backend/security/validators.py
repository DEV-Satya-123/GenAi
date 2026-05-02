"""Input validation and sanitization"""

import re
from urllib.parse import urlparse, unquote
from pathlib import Path
from typing import Optional
from fastapi import HTTPException


class SecurityValidator:
    """Validates and sanitizes user inputs"""
    
    # Allowed Git URL patterns
    GIT_URL_PATTERNS = [
        r'^https://github\.com/[\w\-]+/[\w\-\.]+(?:\.git)?$',
        r'^https://gitlab\.com/[\w\-]+/[\w\-\.]+(?:\.git)?$',
        r'^https://bitbucket\.org/[\w\-]+/[\w\-\.]+(?:\.git)?$',
        r'^git@github\.com:[\w\-]+/[\w\-\.]+\.git$',
        r'^git@gitlab\.com:[\w\-]+/[\w\-\.]+\.git$',
    ]
    
    @staticmethod
    def validate_git_url(url: str) -> str:
        """
        Validate Git URL to prevent command injection
        
        Args:
            url: Git repository URL
            
        Returns:
            Sanitized URL
            
        Raises:
            HTTPException: If URL is invalid or suspicious
        """
        if not url or not isinstance(url, str):
            raise HTTPException(status_code=400, detail="Invalid Git URL")
        
        url = url.strip()
        
        # Check length
        if len(url) > 500:
            raise HTTPException(status_code=400, detail="Git URL too long")
        
        # SECURITY FIX: Decode URL to prevent encoding bypass
        try:
            decoded_url = unquote(url)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid URL encoding")
        
        # Check for suspicious characters in BOTH original and decoded URL
        suspicious_chars = [';', '|', '&', '$', '`', '\n', '\r', '<', '>', '\0', '\x00']
        
        for char in suspicious_chars:
            if char in url or char in decoded_url:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Git URL contains invalid character: {repr(char)}"
                )
        
        # Check for encoded suspicious characters
        suspicious_encoded = ['%3B', '%7C', '%26', '%24', '%60', '%0A', '%0D', '%3C', '%3E', '%00']
        url_upper = url.upper()
        for encoded in suspicious_encoded:
            if encoded in url_upper:
                raise HTTPException(
                    status_code=400, 
                    detail="Git URL contains encoded invalid characters"
                )
        
        # Validate against patterns
        valid = any(re.match(pattern, url) for pattern in SecurityValidator.GIT_URL_PATTERNS)
        if not valid:
            raise HTTPException(
                status_code=400, 
                detail="Invalid Git URL format. Only GitHub, GitLab, and Bitbucket URLs are allowed"
            )
        
        return url
    
    @staticmethod
    def validate_file_path(path: str, base_dir: Optional[str] = None) -> str:
        """
        Validate file path to prevent directory traversal
        
        Args:
            path: File system path
            base_dir: Optional base directory to restrict access
            
        Returns:
            Sanitized absolute path
            
        Raises:
            HTTPException: If path is invalid or attempts traversal
        """
        if not path or not isinstance(path, str):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        path = path.strip()
        
        # Check length
        if len(path) > 1000:
            raise HTTPException(status_code=400, detail="File path too long")
        
        # SECURITY FIX: Decode path to prevent encoding bypass
        try:
            decoded_path = unquote(path)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid path encoding")
        
        # Check for suspicious patterns in BOTH original and decoded path
        suspicious_patterns = ['..', '~', '$', '`', ';', '|', '&', '\n', '\r', '\0']
        
        for pattern in suspicious_patterns:
            if pattern in path or pattern in decoded_path:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File path contains invalid pattern: {repr(pattern)}"
                )
        
        # Check for encoded traversal attempts
        if '%2E%2E' in path.upper() or '%2F%2E%2E' in path.upper():
            raise HTTPException(status_code=400, detail="Path traversal attempt detected")
        
        try:
            # Resolve to absolute path
            abs_path = Path(path).resolve()
            
            # If base_dir specified, ensure path is within it
            if base_dir:
                base_path = Path(base_dir).resolve()
                if not str(abs_path).startswith(str(base_path)):
                    raise HTTPException(
                        status_code=403, 
                        detail="Access denied: Path outside allowed directory"
                    )
            
            return str(abs_path)
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid file path: {str(e)}")
    
    @staticmethod
    def validate_commit_message(message: str) -> str:
        """
        Validate and sanitize commit message
        
        Args:
            message: Commit message
            
        Returns:
            Sanitized message
            
        Raises:
            HTTPException: If message is invalid
        """
        if not message or not isinstance(message, str):
            raise HTTPException(status_code=400, detail="Invalid commit message")
        
        message = message.strip()
        
        # Check length
        if len(message) < 3:
            raise HTTPException(status_code=400, detail="Commit message too short")
        if len(message) > 500:
            raise HTTPException(status_code=400, detail="Commit message too long")
        
        # SECURITY FIX: Decode to check for encoded malicious content
        try:
            decoded_message = unquote(message)
        except Exception:
            decoded_message = message
        
        # Remove control characters
        message = ''.join(char for char in message if ord(char) >= 32 or char == '\n')
        
        # Check for suspicious patterns (command injection attempts) in both
        suspicious_patterns = ['$(', '`', '&&', '||', ';', '|', '\0']
        
        for pattern in suspicious_patterns:
            if pattern in message or pattern in decoded_message:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Commit message contains invalid pattern: {repr(pattern)}"
                )
        
        return message
    
    @staticmethod
    def validate_repo_name(name: str) -> str:
        """
        Validate repository name
        
        Args:
            name: Repository name
            
        Returns:
            Sanitized name
            
        Raises:
            HTTPException: If name is invalid
        """
        if not name or not isinstance(name, str):
            raise HTTPException(status_code=400, detail="Invalid repository name")
        
        name = name.strip()
        
        # Check length
        if len(name) < 1 or len(name) > 100:
            raise HTTPException(status_code=400, detail="Repository name must be 1-100 characters")
        
        # SECURITY FIX: Decode to prevent bypass
        try:
            decoded_name = unquote(name)
        except Exception:
            decoded_name = name
        
        # Only allow alphanumeric, dash, underscore, dot
        if not re.match(r'^[\w\-\.]+$', name):
            raise HTTPException(
                status_code=400, 
                detail="Repository name can only contain letters, numbers, dash, underscore, and dot"
            )
        
        # Check decoded version too
        if not re.match(r'^[\w\-\.]+$', decoded_name):
            raise HTTPException(
                status_code=400, 
                detail="Repository name contains encoded invalid characters"
            )
        
        return name
