# Ultrapilot Skill

Maximum parallel execution with agent teams.

## When to Use
- Large-scale implementations
- Multiple independent features
- Codebase-wide refactoring
- Time-critical parallel work

## When NOT to Use
- Sequential dependencies
- Small changes
- Exploratory work

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                      ULTRAPILOT                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│   │ Agent 1 │  │ Agent 2 │  │ Agent 3 │  │ Agent 4 │       │
│   │  Task A │  │  Task B │  │  Task C │  │  Task D │       │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘       │
│        │            │            │            │             │
│        └────────────┴────────────┴────────────┘             │
│                          │                                   │
│                    ┌─────▼─────┐                            │
│                    │  Merge &  │                            │
│                    │  Verify   │                            │
│                    └───────────┘                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Execution Phases

### 1. Decomposition
- Analyze the task
- Identify independent units
- Check for conflicts
- Assign to agents

### 2. Parallel Execution
- Spawn agent instances
- Execute independently
- Track progress
- Handle failures

### 3. Aggregation
- Collect results
- Resolve conflicts
- Merge changes
- Verify integration

## Agent Allocation

```
ultrapilot 3:executor  → 3 executor agents
ultrapilot 5:mixed     → PM + 4 specialists
ultrapilot auto        → System decides count
```

## Usage

```
ultrapilot: build a fullstack app with auth, dashboard, and API

ultrapilot 5: fix all TypeScript errors across the codebase

ultrapilot: implement CRUD for users, products, and orders
```

## Conflict Resolution

When agents modify the same file:
1. **Detect** - Identify overlapping changes
2. **Analyze** - Determine compatibility
3. **Merge** - Combine compatible changes
4. **Escalate** - Human review if needed

## Best Practices

1. **Clear task boundaries** - Each agent should have distinct scope
2. **Minimize overlap** - Reduce file conflicts
3. **Verify integration** - Test combined output
4. **Monitor progress** - Track all agent status
