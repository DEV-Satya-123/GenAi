"""Security audit logging"""

import logging
from datetime import datetime
from typing import Optional
import json


class AuditLogger:
    """Logs security-relevant events"""
    
    def __init__(self):
        self.logger = logging.getLogger("security.audit")
        self.logger.setLevel(logging.INFO)
        
        # Create file handler for audit logs
        handler = logging.FileHandler("security_audit.log")
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
    
    def log_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[dict] = None,
        success: bool = True
    ):
        """
        Log a security event
        
        Args:
            event_type: Type of event (login, clone, commit, etc.)
            user_id: User identifier
            ip_address: Client IP address
            details: Additional event details
            success: Whether the action succeeded
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id or "anonymous",
            "ip_address": ip_address or "unknown",
            "success": success,
            "details": details or {}
        }
        
        if success:
            self.logger.info(json.dumps(log_entry))
        else:
            self.logger.warning(json.dumps(log_entry))
    
    def log_clone(self, git_url: str, ip_address: str, success: bool = True):
        """Log repository clone attempt"""
        self.log_event(
            event_type="repository_clone",
            ip_address=ip_address,
            details={"git_url": git_url},
            success=success
        )
    
    def log_commit(self, repo_path: str, commit_message: str, ip_address: str, success: bool = True):
        """Log commit attempt"""
        self.log_event(
            event_type="git_commit",
            ip_address=ip_address,
            details={
                "repo_path": repo_path,
                "commit_message": commit_message[:100]  # Truncate
            },
            success=success
        )
    
    def log_push(self, repo_path: str, ip_address: str, success: bool = True):
        """Log push attempt"""
        self.log_event(
            event_type="git_push",
            ip_address=ip_address,
            details={"repo_path": repo_path},
            success=success
        )
    
    def log_security_scan(self, repo_path: str, issues_found: int, ip_address: str):
        """Log security scan"""
        self.log_event(
            event_type="security_scan",
            ip_address=ip_address,
            details={
                "repo_path": repo_path,
                "issues_found": issues_found
            },
            success=True
        )
    
    def log_failed_validation(self, validation_type: str, ip_address: str, details: dict):
        """Log failed input validation"""
        self.log_event(
            event_type="validation_failed",
            ip_address=ip_address,
            details={
                "validation_type": validation_type,
                **details
            },
            success=False
        )


# Global audit logger instance
audit_logger = AuditLogger()
