# Security Check Reference

## SEC-001: Hardcoded Secrets

**Priority:** CRITICAL

**Why it matters:**
Secrets in code get committed to version control, leaked in logs, and exposed in client bundles.

**Bad:**
```javascript
const API_KEY = "sk-1234567890abcdef";
const dbPassword = "admin123";
```

**Good:**
```javascript
const API_KEY = process.env.API_KEY;
const dbPassword = process.env.DB_PASSWORD;
```

**Detection:**
- Look for: `password`, `secret`, `api_key`, `token`, `credential`
- Check for Base64 encoded strings
- Watch for AWS/GCP/Azure key patterns

---

## SEC-002: SQL Injection

**Priority:** CRITICAL

**Why it matters:**
Allows attackers to read, modify, or delete database contents.

**Bad:**
```javascript
const query = `SELECT * FROM users WHERE id = ${userId}`;
db.query(query);
```

**Good:**
```javascript
const query = 'SELECT * FROM users WHERE id = $1';
db.query(query, [userId]);
```

---

## SEC-003: XSS (Cross-Site Scripting)

**Priority:** HIGH

**Why it matters:**
Allows attackers to execute scripts in users' browsers.

**Bad:**
```javascript
element.innerHTML = userInput;
```

**Good:**
```javascript
element.textContent = userInput;
// or use proper sanitization
```

---

## SEC-004: Missing Authentication

**Priority:** HIGH

**Why it matters:**
Unauthenticated endpoints expose sensitive data and actions.

**Check:**
- All API endpoints should verify authentication
- Admin routes need role checks
- File uploads need auth
