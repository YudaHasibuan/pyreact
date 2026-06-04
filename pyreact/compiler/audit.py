"""Security Auditing Engine for PyReact.
Performs static analysis to detect SQL Injection, XSS, and CORS security issues.
"""
import re

class SecurityAuditEngine:
    def __init__(self, filepath: str, source: str):
        self.filepath = filepath
        self.source = source
        self.warnings = []

    def audit(self) -> list:
        lines = self.source.splitlines()
        
        # 1. CORS Wildcard check
        if re.search(r'CORS\([^)]*origins\s*=\s*["\']\*["\']', self.source) or re.search(r'["\']origins["\']\s*:\s*["\']\*["\']', self.source):
            self.warnings.append({
                "type": "CORS Unrestricted",
                "severity": "WARNING",
                "line": 0,
                "msg": "CORS config allows wildcard origins ('*'). For production security, restrict origins to trusted domain origins."
            })

        # 2. Line by line scanning
        for idx, line in enumerate(lines):
            line_no = idx + 1
            
            # SQL Injection Checks
            # Look for SQL keywords with dynamic formatting (+, %, or f-strings)
            sql_keywords = r'(?:SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\b'
            if re.search(sql_keywords, line, re.IGNORECASE):
                # If SQL query is formatted using string formatting/concatenation
                if (
                    "+" in line or 
                    "%" in line or 
                    re.search(r'\b[fF]["\']', line) or
                    ".format(" in line
                ):
                    self.warnings.append({
                        "type": "SQL Injection Risk",
                        "severity": "HIGH",
                        "line": line_no,
                        "msg": "Dynamic string construction of SQL query detected. Use parameterized queries (e.g. executing with bindings) rather than string formatting."
                    })
            
            # Direct execute interpolation check
            if "execute(" in line or ".execute(" in line:
                if (
                    re.search(r'execute\(\s*f["\'].*\{.*\}', line) or
                    re.search(r'execute\(\s*["\'].*["\']\s*\+', line) or
                    re.search(r'execute\(\s*["\'].*%s["\']\s*%', line)
                ):
                    self.warnings.append({
                        "type": "SQL Injection Risk",
                        "severity": "HIGH",
                        "line": line_no,
                        "msg": "String interpolation in SQL execute call. Use parameters (e.g. execute('SELECT * FROM t WHERE k = ?', (v,))) to block SQL injection."
                    })
            
            # XSS Checks
            if "dangerouslySetInnerHTML" in line:
                self.warnings.append({
                    "type": "XSS Vulnerability",
                    "severity": "MEDIUM",
                    "line": line_no,
                    "msg": "Rendered markup with 'dangerouslySetInnerHTML'. Sanitize input variables using clean templates to avoid injection."
                })

        return self.warnings
