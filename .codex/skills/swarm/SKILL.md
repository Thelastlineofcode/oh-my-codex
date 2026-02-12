# Swarm Skill

Legacy multi-agent mode (routes to Team).

## Note

As of v1.0, `swarm` is a compatibility layer that routes to the `team` skill.
Use `team` directly for new projects.

## Legacy Syntax

```
swarm 5 agents: fix all TypeScript errors
swarm 3: implement the dashboard
```

## Equivalent Team Commands

```
team 5:executor fix all TypeScript errors
team 3:mixed implement the dashboard
```

## Why Swarm → Team?

Team provides:
- Staged pipeline execution
- Better coordination
- Built-in verification
- Fix loops

Swarm was simpler parallel execution without these benefits.

## Migration

Replace:
```
swarm N agents: {task}
```

With:
```
team N:executor {task}
```

## Compatibility

Swarm syntax still works and is automatically converted:
- `swarm 5 agents` → `team 5:executor`
- `swarm 3` → `team 3:mixed`
