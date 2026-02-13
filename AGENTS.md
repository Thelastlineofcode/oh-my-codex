# AGENTS.md - Oh My Codex

This file is automatically loaded by Codex CLI and defines how the multi-agent orchestration works.

## Quick Start

Use mode keywords to activate different execution strategies:

| Keyword | Mode | Description |
|---------|------|-------------|
| `autopilot:` | Full orchestration | PM → Architect → Specialists → QA |
| `ulw:` / `ultrawork:` | Parallel execution | Decompose & run in parallel |
| `plan:` | Planning only | Generate detailed plan without execution |
| `eco:` | Token-efficient | Use smaller model for simple tasks |
| `ralph:` | Never give up | Maximum effort with retries |
| `tdd:` | Test-driven | Write tests first, then implement |
| `review:` | Code review | Analyze and suggest improvements |

## Examples

```bash
# Full orchestration
omx "autopilot: build a REST API for user management"

# Parallel execution
omx "ulw: refactor all utility functions"

# Planning only
omx "plan: design a microservices architecture"

# Quick fix (token-efficient)
omx "eco: fix the typo in README"
```

## Agent Roles

When using orchestrated modes, Oh My Codex deploys specialized agents:

### Core Agents
- **PM (Project Manager)** - Coordinates workflow, tracks progress
- **Architect** - Designs system structure and patterns
- **Executor** - Implements code changes

### Specialists
- **Frontend** - React, Vue, CSS, UI/UX
- **Backend** - APIs, databases, server logic
- **DevOps** - CI/CD, deployment, infrastructure
- **QA** - Testing, validation, quality assurance

### Support
- **Analyst** - Requirements analysis, documentation
- **Researcher** - Investigation, best practices
- **Debugger** - Error diagnosis, fixes

## Model Routing

Tasks are automatically routed to appropriate models:

| Complexity | Model | Use Case |
|------------|-------|----------|
| Real-time | gpt-5.3-codex-spark | Simple queries, 1000+ tok/s |
| Simple | gpt-5-codex-mini | Quick fixes, eco mode |
| Standard | gpt-5.2-codex | Default, balanced |
| Complex | gpt-5.3-codex | Autopilot, architecture |
| Maximum | gpt-5.1-codex-max | Ralph, long-running tasks |

## Reasoning Levels

Control thinking depth with reasoning effort:

| Mode | Reasoning | Description |
|------|-----------|-------------|
| eco | none | Fast, no extended thinking |
| plan | medium | Balanced planning |
| autopilot | high | Deep analysis |
| ralph | xhigh | Maximum reasoning (5.3-codex) |

## Custom Instructions

Add your own rules below this line. They will be included in agent context.

---

<!-- Your custom instructions here -->
