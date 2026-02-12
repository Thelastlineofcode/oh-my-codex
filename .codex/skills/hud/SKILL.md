# HUD Skill

Heads-Up Display for real-time orchestration metrics.

## What It Shows

```
┌─────────────────────────────────────────────────────────────────┐
│ OMC │ Mode: autopilot │ Agents: 4 │ Tasks: 12/15 │ Tokens: 45K │
└─────────────────────────────────────────────────────────────────┘
```

## Metrics Displayed

### Mode
```
Current execution mode:
- autopilot
- ultrawork
- team
- eco
- plan
```

### Agent Status
```
Active agents and their status:
- PM: coordinating
- Frontend: executing
- Backend: waiting
- Tester: idle
```

### Task Progress
```
Tasks completed / total:
- 12/15 (80%)
- Current: "Implement user validation"
```

### Token Usage
```
Tokens consumed:
- Current session: 45K
- Estimated remaining: ~20K
- Cost estimate: $0.15
```

### Time
```
Elapsed time:
- Session: 15m 23s
- Current task: 2m 10s
```

## Display Modes

### Minimal (statusline)
```
OMC │ autopilot │ 4 agents │ 80% │ 45K tokens
```

### Standard
```
┌─ Oh My Codex ─────────────────────────────────┐
│ Mode: autopilot    Agents: 4    Progress: 80% │
│ Current: Implement user validation            │
│ Tokens: 45K (~$0.15)    Time: 15m 23s        │
└───────────────────────────────────────────────┘
```

### Detailed
```
╔═══════════════════════════════════════════════════════════════╗
║                     OH MY CODEX HUD                            ║
╠═══════════════════════════════════════════════════════════════╣
║ Mode: autopilot                                                ║
║ Session: 20260213_143022                                       ║
╠───────────────────────────────────────────────────────────────╣
║ AGENTS                                                         ║
║   PM         │ coordinating │ tasks assigned: 15              ║
║   Frontend   │ executing    │ UserForm component              ║
║   Backend    │ waiting      │ -                               ║
║   Tester     │ idle         │ -                               ║
╠───────────────────────────────────────────────────────────────╣
║ PROGRESS                                                       ║
║   [████████████░░░░] 12/15 tasks (80%)                        ║
║   Current: Implement user validation                           ║
╠───────────────────────────────────────────────────────────────╣
║ RESOURCES                                                      ║
║   Tokens: 45,234 (~$0.15)                                     ║
║   Time: 15m 23s                                                ║
║   Model: o3 (85%) | gpt-4.1-mini (15%)                        ║
╚═══════════════════════════════════════════════════════════════╝
```

## Integration

### Terminal Status Bar
Add to your shell prompt or tmux status.

### VS Code Extension
Display in VS Code status bar.

### Web Dashboard
Real-time web view at localhost:8080.

## Usage

```
hud: show current status

hud detail: show detailed metrics

hud watch: continuous monitoring
```

## Configuration

```toml
[hud]
enabled = true
style = "standard"  # minimal | standard | detailed
refresh_ms = 1000
show_cost = true
```
