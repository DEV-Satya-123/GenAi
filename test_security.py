#!/usr/bin/env python3
"""
Test script for the hybrid security scanner (Custom + GitGuardian)
"""

import os
from security.security_scanner import SecurityScanner, SecurityLevel

def test_hybrid_security_scanner():
    # Initialize scanner with GitGuardian API key (if available)
    gitguardian_key = os.getenv('GITGUARDIAN_API_KEY')
    scanner = SecurityScanner(gitguardian_api_key=gitguardian_key)
    
    # Test cases with different security issues
    test_cases = [
        {
            "name": "Safe code change",
            "diff": """
+++ b/src/utils.py
@@ -1,3 +1,6 @@
 def calculate_sum(a, b):
     return a + b
+
+def calculate_product(a, b):
+    return a * b
""",
            "files": ["src/utils.py"]
        },
        {
            "name": "Dangerous .gitignore modification (Custom Scanner)",
            "diff": """
--- a/.gitignore
+++ b/.gitignore
@@ -1,5 +1,4 @@
 node_modules/
 dist/
-.env
 *.log
 .DS_Store
""",
            "files": [".gitignore"]
        },
        {
            "name": "Real AWS secret (GitGuardian will detect)",
            "diff": """
+++ b/config.py
@@ -1,3 +1,4 @@
 DATABASE_URL = "sqlite:///app.db"
+AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
+AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
 DEBUG = True
""",
            "files": ["config.py"]
        },
        {
            "name": "Sensitive file being tracked (Custom Scanner)",
            "diff": """
+++ b/.env
@@ -0,0 +1,3 @@
+DATABASE_URL=postgresql://user:password@localhost/db
+API_KEY=sk-1234567890abcdef
+JWT_SECRET=super_secret_key
""",
            "files": [".env"]
        },
        {
            "name": "GitHub token (GitGuardian detection)",
            "diff": """
+++ b/deploy.sh
@@ -1,3 +1,4 @@
 #!/bin/bash
+export GITHUB_TOKEN="ghp_1234567890abcdefghijklmnopqrstuvwxyz"
 echo "Deploying application..."
""",
            "files": ["deploy.sh"]
        }
    ]
    
    print("🛡️ Hybrid Security Scanner Test Results")
    print("=" * 70)
    
    if gitguardian_key:
        print("🌐 GitGuardian API: ENABLED")
    else:
        print("ℹ️ GitGuardian API: DISABLED (set GITGUARDIAN_API_KEY to enable)")
    
    print("🔧 Custom Scanner: ENABLED")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 50)
        
        issues, level = scanner.scan_diff(test_case['diff'], test_case['files'])
        summary = scanner.get_security_summary(issues, level)
        
        print(f"Security Level: {level.value.upper()}")
        print(f"Issues Found: {len(issues)}")
        print(f"Summary:\n{summary}")
        
        if issues:
            print("\nDetailed Issues:")
            for issue in issues:
                scanner_type = "🌐 GitGuardian" if issue.type == 'gitguardian_detection' else "🔧 Custom"
                print(f"  {scanner_type} • {issue.type}: {issue.message}")
                if issue.suggestion:
                    print(f"    💡 {issue.suggestion}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    test_hybrid_security_scanner()