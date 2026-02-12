# Code Review Skill

Comprehensive code review with security, performance, and quality checks.

## When to Use
- Before merging PRs
- After completing features
- Security audits
- Performance optimization
- Code quality improvement

## Review Categories

| Category | Prefix | Priority | Focus |
|----------|--------|----------|-------|
| Security | SEC- | CRITICAL | Vulnerabilities, auth, data exposure |
| Performance | PERF- | HIGH | Speed, memory, scalability |
| Correctness | BUG- | HIGH | Logic errors, edge cases |
| Maintainability | MAINT- | MEDIUM | Readability, complexity |
| Style | STYLE- | LOW | Formatting, naming |

## Review Process

### 1. Security Review (SEC-)

```
□ No hardcoded secrets
□ Input validation present
□ SQL injection prevention
□ XSS protection
□ CSRF protection
□ Authentication checks
□ Authorization checks
□ Sensitive data handling
□ Secure dependencies
```

### 2. Performance Review (PERF-)

```
□ No N+1 queries
□ Proper indexing
□ Efficient algorithms (O notation)
□ Memory management
□ Caching strategy
□ Bundle size (frontend)
□ Lazy loading
□ Database query optimization
```

### 3. Correctness Review (BUG-)

```
□ Logic is sound
□ Edge cases handled
□ Null/undefined checks
□ Error handling
□ Race conditions
□ State management
□ Type safety
```

### 4. Maintainability Review (MAINT-)

```
□ Single responsibility
□ DRY principle
□ Clear naming
□ Appropriate comments
□ Reasonable complexity
□ Test coverage
□ Documentation
```

## Output Format

```markdown
## Code Review: {scope}

### Summary
{1-2 sentence assessment}

### Critical Issues
- **SEC-001**: {issue}
  - File: {path}:{line}
  - Risk: {description}
  - Fix: {suggestion}

### High Priority
- **PERF-001**: {issue}
  - File: {path}:{line}
  - Impact: {description}
  - Fix: {suggestion}

### Medium Priority
- **MAINT-001**: {issue}
  - Suggestion: {improvement}

### Low Priority
- **STYLE-001**: {issue}

### Positive Notes
- {good practice observed}

### Verdict
[ ] ✅ Approve
[ ] ⚠️ Approve with comments
[ ] ❌ Request changes
```

## Usage

```
review: check the auth module for security issues

code-review: full review of the payment integration

review: performance audit of the dashboard queries
```
