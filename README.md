# Oh My Codex

> Multi-agent orchestration system for OpenAI Codex CLI

Inspired by [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode), built for Codex CLI's architecture.

## Features

- 🧠 **AGENTS.md-First Design** — Core orchestration logic always in context
- 🚀 **5 Execution Modes** — autopilot, ultrawork, plan, eco, review
- 🔧 **Native Skills** — Git, Playwright, Debug, and more
- 🤖 **Multi-Agent Orchestration** — PM + specialists via Codex MCP + Agents SDK
- 📊 **Smart Routing** — Automatic model selection based on task complexity
- 💾 **Session Management** — Pause, resume, track progress

## Quick Start

```bash
# Clone
git clone https://github.com/tarae/oh-my-codex.git
cd oh-my-codex

# Install
./install.sh

# Use
omc "autopilot: build a REST API for tasks"
```

## Installation

### Option 1: Script Install (Recommended)

```bash
./install.sh
```

This installs:
- Skills to `~/.codex/skills/`
- Config to `~/.codex/config.toml`
- CLI wrapper `omc` to `~/.local/bin/`

### Option 2: pip Install

```bash
# Basic
pip install -e .

# With multi-agent support
pip install -e ".[full]"
```

## Usage

### Keywords (Trigger Modes)

```bash
# Autopilot — Full autonomous execution
omc "autopilot: build user authentication with JWT"

# Ultrawork — Parallel multi-file operations
omc "ulw: rename userId to user_id across all files"

# Plan — Interview-driven planning (no execution)
omc "plan: design the payment system architecture"

# Eco — Token-efficient, minimal output
omc "eco: add .env to gitignore"

# Ralph — Persistent autopilot (never gives up)
omc "ralph: fix all TypeScript errors"
```

### Direct Codex

```bash
# No keyword = direct Codex pass-through
omc "fix the bug in auth.py"
```

### Session Management

```bash
# List sessions
omc --list

# Resume a session
omc --resume 20260213_123456_abc12345

# Check status
omc --status
```

## Architecture

```
oh-my-codex/
├── AGENTS.md                 # 🧠 Core orchestration brain
├── .codex/skills/            # 🔧 Native Codex skills
│   ├── autopilot/            # Full autonomous mode
│   ├── ultrawork/            # Parallel execution
│   ├── planner/              # Interview & planning
│   ├── eco/                  # Token-efficient
│   ├── reviewer/             # Code review
│   ├── git-master/           # Git workflows
│   ├── playwright/           # E2E testing
│   └── debug/                # Systematic debugging
├── orchestrator/             # 🤖 Python multi-agent
│   ├── main.py               # Orchestrator entry
│   ├── agents/               # Agent definitions
│   ├── session.py            # Session management
│   ├── mcp.py                # MCP server configs
│   ├── router.py             # Model routing
│   └── utils.py              # Utilities
├── bin/omc                   # CLI wrapper
├── config.toml               # Codex configuration
├── pyproject.toml            # Python package
└── install.sh                # Installer
```

## Execution Modes

| Mode | Keyword | Use Case | Model |
|------|---------|----------|-------|
| **Autopilot** | `autopilot:` | Full feature development | o3 |
| **Ultrawork** | `ulw:` | Parallel refactoring | o3 |
| **Plan** | `plan:` | Architecture design | o3 |
| **Eco** | `eco:` | Quick fixes | gpt-4.1-mini |
| **Review** | (auto) | Code quality check | o3 |

## Design Philosophy

Based on [Vercel's research](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals):

> "AGENTS.md outperforms skills in agent evals" — 100% vs 79% pass rate

**Key insight**: Information always in context beats on-demand retrieval.

Our approach:
1. **AGENTS.md** = Always-present orchestration brain
2. **Skills** = Domain-specific tools (loaded on-demand)
3. **Orchestrator** = Multi-agent coordination layer

## Skills

### Included Skills

| Skill | Description |
|-------|-------------|
| `autopilot` | Autonomous feature development |
| `ultrawork` | Parallel multi-file operations |
| `planner` | Interview-driven planning |
| `eco` | Token-efficient execution |
| `reviewer` | Code review with checklists |
| `git-master` | Git workflow management |
| `playwright` | E2E testing automation |
| `debug` | Systematic debugging |

### Installing External Skills

```bash
# From skills.sh registry
npx skills add supabase/supabase-postgres-best-practices

# Skills are installed to ~/.codex/skills/
```

## Multi-Agent Orchestration

When using `autopilot` or `ultrawork`, Oh My Codex can spawn specialized agents:

```
[Project Manager]
├── [Frontend Developer]  → React, TypeScript, CSS
├── [Backend Developer]   → APIs, databases, auth
├── [QA Tester]           → Tests, edge cases
├── [Code Reviewer]       → Security, quality
└── [Architect]           → System design
```

Requires: `pip install oh-my-codex[full]`

## Configuration

### ~/.codex/config.toml

```toml
[model]
default = "o3"

[model.routing]
simple = "gpt-4.1-mini"
standard = "gpt-4.1"
complex = "o3"

[skills]
auto_load = true

[compaction]
enabled = true
threshold_tokens = 100000
```

### MCP Servers

```toml
[mcp.github]
command = "npx"
args = ["-y", "@anthropic/mcp-server-github"]
env = { GITHUB_TOKEN = "..." }
```

## Roadmap

- [x] Phase 1: Skills + AGENTS.md
- [x] Phase 2: Python orchestrator
- [x] Phase 3: Model routing
- [x] Phase 4: CLI wrapper (`omc`)
- [ ] Phase 5: Native Codex plugin (waiting for Codex plugin system)

## Contributing

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## Credits

- [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) — Original inspiration
- [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) — Architecture reference
- [Supabase Agent Skills](https://github.com/supabase/agent-skills) — Skill structure
- [Vercel AGENTS.md Research](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) — Design philosophy

## License

MIT
