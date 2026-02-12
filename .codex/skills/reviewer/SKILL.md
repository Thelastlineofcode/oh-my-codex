# Reviewer Skill

Code review with structured feedback.

## When to Use
- Before merging PRs
- After completing a feature (self-review)
- When user asks for code review
- Quality gate checks

## When NOT to Use
- During active development (let them finish first)
- For trivial changes
- When user explicitly skips review

## Review Categories

| Category | Prefix | Priority |
|----------|--------|----------|
| Security | SEC- | CRITICAL |
| Performance | PERF- | HIGH |
| Correctness | BUG- | HIGH |
| Maintainability | MAINT- | MEDIUM |
| Style | STYLE- | LOW |

## Workflow

```
1. SCAN
   - Read all changed files
   - Understand the intent

2. ANALYZE
   - Check each category
   - Note issues with severity

3. REPORT
   - Group by severity
   - Provide actionable feedback
   - Suggest fixes, not just problems

4. SUMMARIZE
   - Overall assessment
   - Blocking vs non-blocking issues
```

## Review Output Format

```markdown
## Code Review: {scope}

### Summary
{1-2 sentence overall assessment}

### Critical Issues
- **SEC-001**: {issue}
  - File: {path}:{line}
  - Fix: {suggestion}

### High Priority
- **PERF-001**: {issue}
  - File: {path}:{line}
  - Fix: {suggestion}

### Suggestions
- **MAINT-001**: {issue}
  - {suggestion}

### Verdict
[ ] ✅ Approve
[ ] ⚠️ Approve with comments
[ ] ❌ Request changes
```

## Security Checklist (SEC-)
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] SQL injection protection
- [ ] XSS prevention
- [ ] Auth checks in place

## Performance Checklist (PERF-)
- [ ] No N+1 queries
- [ ] Appropriate indexing
- [ ] No memory leaks
- [ ] Efficient algorithms

## See Also
- references/security-check.md
- references/performance-check.md
- references/style-check.md
