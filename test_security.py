#!/usr/bin/env python3
"""
Quick test script for the security scanner
"""

from security.security_scanner import SecurityScanner, SecurityLevel

def test_security_scanner():
    scanner = SecurityScanner()
    
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
            "name": "API key detected",
            "diff": """
+++ b/config.py
@@ -1,3 +1,4 @@
 DATABASE_URL = "sqlite:///app.db"
+API_KEY = "sk-1234567890abcdef1234567890abcdef"
 DEBUG = True
""",
            "files": ["config.py"]
        },
        {
            "name": "Database password",
            "diff": """
+++ b/settings.py
@@ -1,3 +1,4 @@
 HOST = "localhost"
+PASSWORD = "super_secret_password"
 PORT = 5432
""",
            "files": ["settings.py"]
        },
        {
            "name": "Private key",
            "diff": """
+++ b/keys/private.key
@@ -0,0 +1,5 @@
+-----BEGIN PRIVATE KEY-----
+MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7...
+-----END PRIVATE KEY-----
""",
            "files": ["keys/private.key"]
        }
    ]
    
    print("🛡️ Security Scanner Test Results")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['name']}")
        print("-" * 30)
        
        issues, level = scanner.scan_diff(test_case['diff'], test_case['files'])
        summary = scanner.get_security_summary(issues, level)
        
        print(f"Security Level: {level.value.upper()}")
        print(f"Issues Found: {len(issues)}")
        print(f"Summary:\n{summary}")
        
        if issues:
            print("\nDetailed Issues:")
            for issue in issues:
                print(f"  • {issue.type}: {issue.message}")
                if issue.suggestion:
                    print(f"    Suggestion: {issue.suggestion}")

if __name__ == "__main__":
    test_security_scanner()