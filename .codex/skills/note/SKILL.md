# Note Skill

In-session note taking and context preservation.

## When to Use
- Recording decisions during development
- Tracking TODOs and ideas
- Preserving context for later
- Documenting discoveries

## Note Types

### Decision Notes
```markdown
## Decision: {title}
Date: {date}
Status: Decided | Pending | Superseded

### Context
{Why did this come up?}

### Options Considered
1. {Option A} - {pros/cons}
2. {Option B} - {pros/cons}

### Decision
{What was decided and why}

### Consequences
- {impact 1}
- {impact 2}
```

### TODO Notes
```markdown
## TODO: {title}
Priority: High | Medium | Low
Status: Open | In Progress | Done

### Description
{What needs to be done}

### Context
{Why it matters}

### Acceptance Criteria
- [ ] {criterion 1}
- [ ] {criterion 2}
```

### Discovery Notes
```markdown
## Discovery: {title}
Date: {date}

### Finding
{What was discovered}

### Location
{Where in codebase}

### Implications
{What this means for the project}

### Action Items
- {action}
```

### Context Notes
```markdown
## Context: {topic}
Session: {session_id}

### Background
{Relevant background info}

### Current State
{Where we are now}

### Next Steps
{What comes next}
```

## Storage

```
.codex/
├── notes/
│   ├── decisions/
│   ├── todos/
│   ├── discoveries/
│   └── context/
└── sessions/
    └── {session_id}/
        └── notes.md
```

## Commands

```
note: we decided to use PostgreSQL over MongoDB for ACID compliance

note todo: add input validation to the user form

note discovery: found undocumented API endpoint at /internal/metrics

note context: auth system uses JWT with 15min expiry
```

## Session Integration

Notes are automatically:
1. Timestamped
2. Linked to session
3. Searchable
4. Persistent across sessions

## Quick Reference

| Command | Action |
|---------|--------|
| `note:` | General note |
| `note todo:` | Add TODO |
| `note decision:` | Record decision |
| `note discovery:` | Document finding |
| `note context:` | Save context |
