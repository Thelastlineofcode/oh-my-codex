# Trace Skill

Execution tracing and debugging for orchestration.

## When to Use
- Debugging agent behavior
- Understanding decision flow
- Performance profiling
- Troubleshooting failures

## Trace Levels

### Level 1: Summary
```
[15:30:01] Task started: "Build auth system"
[15:30:05] Plan created: 5 subtasks
[15:35:22] All tasks completed
[15:35:23] Session ended: SUCCESS
```

### Level 2: Standard
```
[15:30:01] PM: Received task "Build auth system"
[15:30:02] PM: Analyzing requirements...
[15:30:05] PM: Created plan with 5 subtasks
[15:30:06] PM: Delegating to Frontend (subtask 1)
[15:30:06] PM: Delegating to Backend (subtask 2)
[15:31:15] Frontend: Completed "Login form"
[15:32:30] Backend: Completed "Auth API"
...
```

### Level 3: Verbose
```
[15:30:01.234] PM: Received task
  Input: "Build auth system"
  Context: {session: "abc123", mode: "autopilot"}
  
[15:30:02.456] PM: Calling model
  Model: o3
  Tokens: 1,234 (prompt) + 567 (completion)
  Latency: 2.3s
  
[15:30:05.789] PM: Plan generated
  Plan: {
    tasks: [
      {id: 1, description: "Login form", agent: "frontend"},
      ...
    ]
  }
```

## Trace Output

### Console
```
Real-time output to terminal
```

### File
```
Written to ~/.codex/traces/{session_id}.log
```

### Structured (JSON)
```json
{
  "timestamp": "2026-02-13T15:30:01.234Z",
  "agent": "pm",
  "event": "task_received",
  "data": {
    "task": "Build auth system",
    "mode": "autopilot"
  }
}
```

## Trace Events

| Event | Description |
|-------|-------------|
| `task_received` | Agent received a task |
| `task_delegated` | Task assigned to another agent |
| `task_started` | Agent began work |
| `task_completed` | Agent finished work |
| `task_failed` | Agent encountered error |
| `model_call` | LLM API called |
| `tool_used` | Tool executed |
| `decision` | Agent made decision |

## Analysis

### Timeline View
```
PM          ████░░░░░░░░░░░░░░░░░░░░░░
Frontend    ░░░░████████░░░░░░░░░░░░░░
Backend     ░░░░████████████░░░░░░░░░░
Tester      ░░░░░░░░░░░░░░░░████░░░░░░
            0s  5s  10s 15s 20s 25s 30s
```

### Token Usage
```
Agent       Tokens    Cost
PM          12,345    $0.05
Frontend    8,234     $0.03
Backend     15,678    $0.06
Tester      4,567     $0.02
────────────────────────────
Total       40,824    $0.16
```

## Usage

```
trace: enable tracing for this session

trace verbose: detailed tracing

trace analyze: show trace analysis for last session
```

## Configuration

```toml
[trace]
enabled = false  # Enable with trace: command
level = "standard"  # summary | standard | verbose
output = ["console", "file"]
format = "text"  # text | json
```
