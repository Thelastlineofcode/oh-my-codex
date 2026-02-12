# Security Review Skill

Focused security audit for code and architecture.

## When to Use
- Before deploying to production
- After adding authentication/authorization
- When handling sensitive data
- Regular security audits
- Compliance requirements

## OWASP Top 10 Checklist

### 1. Broken Access Control
```
□ Authentication on all protected routes
□ Authorization checks for resources
□ No direct object references exposed
□ CORS properly configured
□ JWT validation complete
```

### 2. Cryptographic Failures
```
□ Sensitive data encrypted at rest
□ TLS for data in transit
□ Strong hashing for passwords (bcrypt, argon2)
□ No hardcoded secrets
□ Proper key management
```

### 3. Injection
```
□ Parameterized queries (no string concat)
□ Input validation
□ Output encoding
□ ORM used correctly
□ Command injection prevention
```

### 4. Insecure Design
```
□ Threat modeling done
□ Security requirements defined
□ Secure defaults
□ Defense in depth
□ Least privilege principle
```

### 5. Security Misconfiguration
```
□ Default credentials changed
□ Unnecessary features disabled
□ Error messages don't leak info
□ Security headers set
□ Dependencies up to date
```

### 6. Vulnerable Components
```
□ Dependencies scanned (npm audit, etc.)
□ Known vulnerabilities addressed
□ Components from trusted sources
□ Unused dependencies removed
```

### 7. Auth Failures
```
□ Strong password requirements
□ Rate limiting on auth endpoints
□ Session management secure
□ Multi-factor available
□ Secure password reset
```

### 8. Data Integrity Failures
```
□ Integrity verification for data
□ Signed updates/packages
□ CI/CD pipeline secured
□ Serialization safe
```

### 9. Logging Failures
```
□ Security events logged
□ Logs don't contain secrets
□ Log injection prevented
□ Monitoring/alerting set up
```

### 10. SSRF
```
□ URL validation
□ Allowlist for external calls
□ Network segmentation
□ Metadata endpoint blocked
```

## Quick Checks

### Secrets
```bash
# Look for hardcoded secrets
grep -r "password\|secret\|api_key\|token" --include="*.ts" --include="*.js"
```

### SQL Injection
```javascript
// BAD
db.query(`SELECT * FROM users WHERE id = ${userId}`)

// GOOD
db.query('SELECT * FROM users WHERE id = $1', [userId])
```

### XSS
```javascript
// BAD
element.innerHTML = userInput

// GOOD
element.textContent = userInput
```

## Usage

```
security-review: audit the authentication system

security: check the API for injection vulnerabilities

security-review: full OWASP Top 10 audit
```

## Output Format

```markdown
## Security Review: {scope}

### Critical Vulnerabilities
🔴 **SEC-CRIT-001**: {vulnerability}
   - CWE: {cwe-id}
   - Location: {file}:{line}
   - Risk: {impact}
   - Remediation: {fix}

### High Risk
🟠 **SEC-HIGH-001**: {issue}

### Medium Risk  
🟡 **SEC-MED-001**: {issue}

### Recommendations
- {best practice suggestion}

### Compliance Notes
- {relevant compliance info}
```
