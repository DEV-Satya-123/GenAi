#!/usr/bin/env python3
"""
Quick test script for the enhanced security scanner
"""

from security.security_scanner import SecurityScanner, SecurityLevel

def test_enhanced_security_scanner():
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
            "name": "Dangerous .gitignore modification",
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
            "name": "Sensitive file being tracked",
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
            "name": "Private key file added",
            "diff": """
+++ b/keys/id_rsa
@@ -0,0 +1,5 @@
+-----BEGIN PRIVATE KEY-----
+MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7...
+-----END PRIVATE KEY-----
""",
            "files": ["keys/id_rsa"]
        },
        {
            "name": "Multiple gitignore patterns removed",
            "diff": """
--- a/.gitignore
+++ b/.gitignore
@@ -1,8 +1,5 @@
 node_modules/
 dist/
-.env
-.env.local
-*.key
-*.pem
 *.log
 .DS_Store
""",
            "files": [".gitignore"]
        }
    ]
    
    print("🛡️ Enhanced Security Scanner Test Results")
    print("=" * 60)
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['name']}")
        print("-" * 40)
        
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
                    print(f"    💡 {issue.suggestion}")

if __name__ == "__main__":
    test_enhanced_security_scanner()