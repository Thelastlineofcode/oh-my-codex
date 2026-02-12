# Debug Skill

Systematic debugging and troubleshooting.

## When to Use
- Unexpected errors or behavior
- Performance issues
- Intermittent failures
- Complex bugs that resist simple fixes

## When NOT to Use
- Clear, simple errors with obvious fixes
- Feature development (use autopilot)

## Debugging Methodology

### 1. REPRODUCE
Before fixing anything:
- Get exact steps to reproduce
- Identify if it's consistent or intermittent
- Note environment (OS, browser, versions)
- Capture error messages verbatim

### 2. ISOLATE
Narrow down the problem:
- Binary search through code/commits
- Remove components until bug disappears
- Check if bug exists in isolation

### 3. HYPOTHESIZE
Form theories:
- What changed recently?
- What assumptions might be wrong?
- What are the edge cases?

### 4. TEST
Verify hypothesis:
- Add logging/breakpoints
- Write failing test
- Check in debugger

### 5. FIX
Apply minimal fix:
- Fix root cause, not symptoms
- Don't introduce new bugs
- Add regression test

### 6. VERIFY
Confirm fix:
- Original bug is gone
- No new bugs introduced
- Tests pass

## Common Bug Patterns

### Off-by-One
```javascript
// Bug: skips last item
for (let i = 0; i < arr.length - 1; i++)

// Fix:
for (let i = 0; i < arr.length; i++)
```

### Null/Undefined
```javascript
// Bug: crashes on null
user.profile.name

// Fix: optional chaining
user?.profile?.name
```

### Async Race Condition
```javascript
// Bug: uses stale data
setData(await fetch('/api'));
doSomething(data); // data not updated yet

// Fix: use returned value
const newData = await fetch('/api');
setData(newData);
doSomething(newData);
```

### State Mutation
```javascript
// Bug: mutates original
const sorted = arr.sort();

// Fix: copy first
const sorted = [...arr].sort();
```

### Closure Capture
```javascript
// Bug: all callbacks use final i
for (var i = 0; i < 5; i++) {
  setTimeout(() => console.log(i), 100);
}

// Fix: use let or IIFE
for (let i = 0; i < 5; i++) {
  setTimeout(() => console.log(i), 100);
}
```

## Debugging Tools

### Console Methods
```javascript
console.log(value);           // Basic output
console.table(array);         // Tabular data
console.trace();              // Stack trace
console.time('label');        // Start timer
console.timeEnd('label');     // End timer
console.group('label');       // Group logs
console.groupEnd();
```

### Node.js Debugging
```bash
# Inspect mode
node --inspect app.js

# Break on first line
node --inspect-brk app.js

# Using Chrome DevTools
# Open chrome://inspect
```

### Git Bisect
```bash
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
# Git checks out middle commit
# Test and mark:
git bisect good  # or
git bisect bad
# Repeat until found
git bisect reset
```

## Log Analysis

### Patterns to Look For
- Timestamps around failure
- Error messages and stack traces
- Unusual patterns (spikes, gaps)
- Correlation with other events

### Log Levels
```
ERROR: Something failed, needs attention
WARN:  Something unexpected, may cause issues
INFO:  Normal operations
DEBUG: Detailed troubleshooting info
```

## Questions to Ask

1. When did this start happening?
2. What changed around that time?
3. Does it happen in all environments?
4. Can you reproduce it consistently?
5. What's the exact error message?
6. What did you expect to happen?
7. What actually happened?
