# Style Check Reference

## STYLE-001: Inconsistent Naming

**Priority:** LOW

**Conventions:**
- JavaScript/TypeScript: camelCase for variables, PascalCase for classes/components
- Python: snake_case for variables/functions, PascalCase for classes
- Constants: SCREAMING_SNAKE_CASE

---

## STYLE-002: Dead Code

**Priority:** LOW

**What to look for:**
- Commented-out code blocks
- Unused imports
- Unreachable code after return/throw
- Unused variables

**Note:** Sometimes kept intentionally for reference. Ask before removing.

---

## STYLE-003: Long Functions

**Priority:** LOW

**Rule of thumb:**
- Functions over 50 lines should probably be split
- If you can't describe what it does in one sentence, split it

---

## STYLE-004: Magic Numbers

**Priority:** LOW

**Bad:**
```javascript
if (status === 3) { ... }
setTimeout(fn, 86400000);
```

**Good:**
```javascript
const STATUS_COMPLETED = 3;
if (status === STATUS_COMPLETED) { ... }

const ONE_DAY_MS = 24 * 60 * 60 * 1000;
setTimeout(fn, ONE_DAY_MS);
```
