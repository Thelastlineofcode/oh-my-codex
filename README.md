# Oh My Codex

<p align="center">
  <strong>🚀 Multi-agent orchestration for OpenAI Codex CLI</strong><br>
  <em>Turn Codex into a team of AI agents</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/oh-my-codex/"><img src="https://img.shields.io/pypi/v/oh-my-codex" alt="PyPI"></a>
  <a href="https://github.com/junghwaYang/oh-my-codex/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://github.com/junghwaYang/oh-my-codex"><img src="https://img.shields.io/github/stars/junghwaYang/oh-my-codex" alt="Stars"></a>
</p>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#execution-modes">Modes</a> •
  <a href="#agents">Agents</a> •
  <a href="#tools">Tools</a> •
  <a href="README.ko.md">한국어</a>
</p>

---

## Why Oh My Codex?

Codex CLI is powerful alone. **Oh My Codex makes it a team.**

| Codex CLI | Oh My Codex |
|-----------|-------------|
| Single agent | 32 specialized agents |
| Manual model selection | Auto model routing |
| Sequential execution | Parallel execution |
| No session memory | Session persistence |

Based on [Vercel's research](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals): **AGENTS.md achieves 100% pass rate** vs 79% for skills-only.

## Installation

### Option 1: PyPI (Recommended)

```bash
pip install oh-my-codex
omx-setup  # Interactive setup wizard
```

### Option 2: pip with full orchestration

```bash
pip install oh-my-codex[full]  # Includes OpenAI Agents SDK
omx-setup
```

### Option 3: From Source

```bash
git clone https://github.com/junghwaYang/oh-my-codex.git
cd oh-my-codex
./install.sh
```

### Option 4: uv (fast)

```bash
uv pip install oh-my-codex[full]
omx-setup
```

### Requirements

- Python 3.10+
- [Codex CLI](https://github.com/openai/codex) installed (`npm i -g @openai/codex`)
- OpenAI API key or Codex Pro subscription

## Quick Start

```bash
# Basic usage (direct Codex)
omx "fix the bug in auth.py"

# Multi-agent autonomous execution
omx "autopilot: build a REST API with auth"

# Parallel execution
omx "ulw: refactor all components to TypeScript"

# Never give up mode
omx "ralph: fix all failing tests"
```

## Execution Modes

| Keyword | Mode | Description | Agents |
|---------|------|-------------|--------|
| `autopilot:` | Autopilot | Full autonomous execution | PM → Executor → Tester → Reviewer |
| `ulw:` | Ultrawork | Parallel multi-agent | PM + Frontend + Backend + Tester |
| `ultrapilot:` | Ultrapilot | Maximum parallelism | All specialists |
| `team:` | Team | Pipeline orchestration | plan → exec → verify → fix loop |
| `ralph:` | Ralph | Persistent (never gives up) | PM → Executor → Debugger |
| `plan:` | Plan | Planning only, no execution | Planner + Architect |
| `eco:` | Eco | Token-efficient, fast | Single Executor |
| `tdd:` | TDD | Test-driven development | Tester → Executor |
| `review:` | Review | Code review | Reviewer + Security |
| `debug:` | Debug | Systematic debugging | Debugger + Analyst |

### Examples

```bash
# Complex feature development
omx "autopilot: implement OAuth2 with Google and GitHub"

# Parallel refactoring
omx "ulw: convert all class components to hooks"

# Persistent bug fixing
omx "ralph: the login redirect isn't working, fix it"

# Architecture planning
omx "plan: design a microservices architecture"

# Quick fix (token-efficient)
omx "eco: add error handling to api calls"

# Test-driven development
omx "tdd: implement password validation"

# Security review
omx "review: audit the authentication module"
```

## Models & Reasoning

### Auto Model Selection

| Task Complexity | Model |
|-----------------|-------|
| Trivial | gpt-5-nano |
| Simple | gpt-5-mini |
| Standard | gpt-5.1-codex |
| Complex | gpt-5.2-codex |
| Long-running | gpt-5.1-codex-max |

### Reasoning Effort

| Level | Usage | Auto-mapped Modes |
|-------|-------|-------------------|
| `none` | Fast responses | eco |
| `low` | Light tasks | tdd, pipeline |
| `medium` | Balanced | plan, ultrawork |
| `high` | Deep thinking | autopilot, review |
| `xhigh` | Maximum (5.2-codex) | ralph, ultrapilot, debug |

```bash
# Manual override
omx --reasoning xhigh "complex architecture decision"
omx --model gpt-5.2-codex "critical task"
```

## Agents (32)

### Orchestration
| Agent | Model | Role |
|-------|-------|------|
| PM | gpt-5.2-codex | Master orchestrator, delegates tasks |
| Coordinator | gpt-5.2-codex | Manages parallel execution |
| Executor | gpt-5.1-codex | Gets things done |

### Development
| Agent | Expertise |
|-------|-----------|
| Frontend | React, Vue, TypeScript, CSS |
| Backend | Node.js, Python, APIs, DBs |
| Fullstack | End-to-end development |
| Mobile | React Native, Flutter |
| DevOps | CI/CD, Docker, K8s |

### Quality
| Agent | Focus |
|-------|-------|
| Tester | Unit, integration, E2E tests |
| Reviewer | Code review, best practices |
| Security | Vulnerabilities, OWASP |
| Debugger | Systematic bug hunting |

### Specialized
| Agent | Domain |
|-------|--------|
| Architect | System design, patterns |
| Researcher | Information gathering |
| Data/ML | Data engineering, ML |
| Writer | Documentation |

## Tools (9)

Agents have access to these tools:

| Tool | Description |
|------|-------------|
| `run_shell` | Execute terminal commands |
| `read_file` | Read file contents |
| `write_file` | Create/overwrite files |
| `edit_file` | Precise text replacement |
| `list_directory` | Browse directories |
| `search_files` | Find files by name/content |
| `git_status` | Check git state |
| `git_diff` | View changes |
| `run_tests` | Auto-detect & run tests |

## Skills (31)

Installed to `~/.codex/skills/`:

| Category | Skills |
|----------|--------|
| Orchestration | team, autopilot, ultrawork, ultrapilot, ralph, pipeline, swarm |
| Planning | planner, ralplan, analyze, research, deepsearch |
| Development | eco, tdd, build-fix, deepinit, release |
| Quality | reviewer, code-review, security-review, ultraqa |
| Utilities | git-master, playwright, debug, mcp-setup, doctor, hud, trace |

## CLI Reference

```bash
# Basic
omx "task"                      # Auto-detect mode
omx "autopilot: task"           # Explicit mode

# Options
omx --model gpt-5.2-codex "task"  # Model override
omx --reasoning high "task"       # Reasoning level
omx --provider openai "task"      # Use API billing
omx -v "task"                     # Verbose output

# Sessions
omx --list                      # List all sessions
omx --resume <session_id>       # Resume session
omx --status                    # Show current config

# Setup
omx-setup                       # Run setup wizard
omx --set-provider codex        # Change billing
```

## Configuration

### ~/.codex/omx-config.yaml

```yaml
billing:
  provider: codex  # or "openai"

model:
  default: gpt-5.1-codex
  routing:
    nano: gpt-5-nano
    mini: gpt-5-mini
    standard: gpt-5.1-codex
    powerful: gpt-5.2-codex
    max: gpt-5.1-codex-max
  reasoning:
    default: none
    autopilot: high
    ralph: xhigh
    eco: none

skills:
  auto_load: true
```

## Architecture

```
User: omx "autopilot: build API"
         │
         ▼
    ┌─────────────┐
    │ Mode Detect │ → autopilot
    │ Model Route │ → gpt-5.2-codex
    │ Reasoning   │ → high
    └──────┬──────┘
           ▼
    ┌─────────────┐
    │ PM Agent    │ ← tools: shell, files, git
    │ + Handoffs  │ → [Executor, Tester, Reviewer]
    └──────┬──────┘
           ▼
    ┌─────────────┐
    │ Runner.run  │ ← OpenAI Agents SDK
    │ Autonomous  │
    └──────┬──────┘
           ▼
       Results
```

## Comparison

| Feature | Codex CLI | omx |
|---------|-----------|-----|
| Single agent | ✅ | ✅ |
| Multi-agent | ❌ | ✅ 32 agents |
| Parallel execution | ❌ | ✅ ultrawork |
| Auto model routing | ❌ | ✅ |
| Reasoning control | Manual | ✅ Auto-mapped |
| Session persistence | ❌ | ✅ |
| Skills | ✅ | ✅ 31 included |

## Credits

- [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) — Original inspiration
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) — Multi-agent framework
- [Vercel Research](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) — AGENTS.md philosophy

## License

MIT © [junghwaYang](https://github.com/junghwaYang)
