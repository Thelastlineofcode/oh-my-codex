# Autopilot Skill

Autonomous execution mode for building features end-to-end.

## When to Use
- Building new features from scratch
- Implementing complete user stories
- Complex refactoring across multiple files
- Any task that benefits from systematic planning

## When NOT to Use
- Simple one-line fixes
- Quick typo corrections
- Tasks where user wants step-by-step control
- Debugging sessions (use direct interaction)

## Workflow

```
1. UNDERSTAND
   - Parse the request completely
   - Identify acceptance criteria
   - List unknowns and assumptions

2. PLAN
   - Break into atomic tasks
   - Identify file dependencies
   - Estimate complexity per task
   - Save plan to .codex/plans/{task-id}.md

3. EXECUTE
   - Work through tasks sequentially
   - Commit after each logical unit
   - Log progress to .codex/sessions/

4. VERIFY
   - Run tests if available
   - Check against acceptance criteria
   - Self-review for obvious issues

5. ITERATE
   - If verification fails, fix and re-verify
   - Max 3 self-fix attempts before asking user
```

## Plan Template

```markdown
# Task: {title}

## Acceptance Criteria
- [ ] {criterion 1}
- [ ] {criterion 2}

## Tasks
1. {task 1} - {file(s)} - {complexity: S/M/L}
2. {task 2} - {file(s)} - {complexity: S/M/L}

## Dependencies
- {task 2} depends on {task 1}

## Risks
- {potential issue}
```

## Commit Message Format

```
{type}({scope}): {description}

- {detail 1}
- {detail 2}

[autopilot]
```

Types: feat, fix, refactor, docs, test, chore

## Examples

**Good trigger:**
> "autopilot: build a user authentication system with JWT"

**Bad trigger (use direct instead):**
> "fix the typo in README"
