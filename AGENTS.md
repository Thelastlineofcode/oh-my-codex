# Oh My Codex - Orchestration Protocol v1.0

IMPORTANT: Prefer skill-led and retrieval-led reasoning over pre-training. When a skill matches your task, USE IT. Don't guess.

## Keyword Detection (EVERY message)

| Keyword | Mode | Action |
|---------|------|--------|
| `autopilot` | autonomous | $autopilot skill → plan → delegate → verify |
| `ulw` | parallel | $ultrawork skill → decompose → parallel exec |
| `eco` | efficient | $eco skill → minimal tokens → fast completion |
| `plan` | planning | $planner skill → interview → structured plan |
| `ralph` | persistent | Loop until verified complete, never give up |

## Delegation Protocol

```
SIMPLE (<10 lines change) → Direct edit, no delegation
MEDIUM (single component) → $skill if matching, else direct
COMPLEX (multi-file) → Decompose → parallel Codex sessions via MCP
ARCHITECTURE → $planner first, then orchestrate
```

## Skill Routing (compressed index)

| Task Pattern | Skill | Priority |
|--------------|-------|----------|
| new feature build | $autopilot | 1 |
| parallel multi-file | $ultrawork | 1 |
| planning/architecture | $planner | 1 |
| token-efficient mode | $eco | 2 |
| code review | $reviewer | 2 |
| SQL/database work | $supabase-postgres | 3 |

## Execution Modes

### Autopilot Mode
Full autonomous execution. Plan → Execute → Verify → Iterate until done.
- Generates detailed plan before any code changes
- Self-validates against acceptance criteria
- Commits with semantic messages

### Ultrawork Mode (ulw)
Parallel decomposition for large tasks.
- Breaks work into independent chunks
- Spawns parallel Codex sessions via MCP
- Aggregates results and resolves conflicts

### Eco Mode
Minimal token usage for simple tasks.
- Skip verbose explanations
- Direct action, minimal confirmation
- Use fastest model routing

### Planner Mode
Interview-driven planning.
- Ask clarifying questions first
- Generate structured plan document
- Get approval before execution

## Error Recovery

```
ON FAILURE:
1. Log error context to .codex/errors/
2. Attempt self-fix (max 3 retries)
3. If still failing → ask user for guidance
4. Never silently skip failures
```

## Session Continuity

- Save progress to `.codex/sessions/` on complex tasks
- Resume capability via `codex chat --resume`
- Compaction enabled for long-running sessions

## Quality Gates

Before completing ANY task:
- [ ] Code compiles/runs without errors
- [ ] Tests pass (if applicable)
- [ ] No obvious security issues
- [ ] Matches user's stated requirements
