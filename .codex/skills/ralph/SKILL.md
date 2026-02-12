# Ralph Skill

Persistent execution mode that never gives up.

## When to Use
- Tasks that MUST complete fully
- Stubborn bugs that resist fixing
- Complex refactoring with many errors
- Any task where partial completion is unacceptable

## When NOT to Use
- Exploratory work
- Tasks where "good enough" is acceptable
- Time-sensitive quick fixes

## Philosophy

Ralph is named after the "ralph mode" concept: relentless persistence.

```
"Never give up. Never surrender."
```

## Workflow

```
1. ATTEMPT
   Execute the task

2. VERIFY
   Check if truly complete
   - All tests pass?
   - No errors remaining?
   - Meets all criteria?

3. FIX (if needed)
   Address failures
   
4. LOOP
   Repeat until verified complete
   (No max attempts - ralph doesn't quit)
```

## Verification Checklist

Before declaring complete:
- [ ] Code compiles without errors
- [ ] All tests pass
- [ ] No TypeScript/lint errors
- [ ] Functionality verified
- [ ] Edge cases handled

## Usage

```
ralph: fix all TypeScript errors in the project

ralph: refactor the auth module to use the new API

ralph: migrate all components to the new design system
```

## Behavior

1. **No partial completion** - Either fully done or still working
2. **Self-healing** - Automatically fixes issues it creates
3. **Progress tracking** - Reports status regularly
4. **Escalation** - Only asks for help when truly stuck

## Notes

- Ralph includes ultrawork capabilities (parallel execution)
- Combines persistence with efficiency
- Will loop indefinitely until success
- Use for critical tasks only (token-intensive)
