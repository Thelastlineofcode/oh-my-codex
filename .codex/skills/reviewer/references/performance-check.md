# Performance Check Reference

## PERF-001: N+1 Query Problem

**Priority:** HIGH

**Why it matters:**
Executing N queries in a loop instead of 1 batched query. Destroys performance at scale.

**Bad:**
```javascript
const users = await db.query('SELECT * FROM users');
for (const user of users) {
  const posts = await db.query('SELECT * FROM posts WHERE user_id = ?', [user.id]);
  user.posts = posts;
}
```

**Good:**
```javascript
const users = await db.query('SELECT * FROM users');
const userIds = users.map(u => u.id);
const posts = await db.query('SELECT * FROM posts WHERE user_id = ANY(?)', [userIds]);
// Then group posts by user_id
```

---

## PERF-002: Missing Database Indexes

**Priority:** HIGH

**Why it matters:**
Queries on unindexed columns cause full table scans.

**Check:**
- Foreign keys should be indexed
- Columns in WHERE clauses need indexes
- Columns used in ORDER BY should be indexed

**How to verify:**
```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
-- Look for "Seq Scan" (bad) vs "Index Scan" (good)
```

---

## PERF-003: Memory Leaks

**Priority:** HIGH

**Patterns to watch:**
- Event listeners not removed
- Intervals not cleared
- Growing arrays/maps without bounds
- Closures holding references

**Bad:**
```javascript
useEffect(() => {
  window.addEventListener('resize', handleResize);
  // Missing cleanup!
}, []);
```

**Good:**
```javascript
useEffect(() => {
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []);
```

---

## PERF-004: Inefficient Algorithms

**Priority:** MEDIUM

**Common issues:**
- O(n²) when O(n) is possible
- Repeated calculations (memoize!)
- Unnecessary re-renders in React
