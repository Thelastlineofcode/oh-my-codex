# Oh My Codex

<p align="center">
  <strong>Multi-agent orchestration system for OpenAI Codex CLI</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#execution-modes">Modes</a> •
  <a href="#skills">Skills</a> •
  <a href="#multi-agent-orchestration">Multi-Agent</a> •
  <a href="README.ko.md">한국어</a>
</p>

---

Inspired by [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode), adapted for OpenAI Codex CLI's architecture.

## Why Oh My Codex?

OpenAI Codex CLI is powerful, but lacks the multi-agent orchestration capabilities that make Claude Code + oh-my-claudecode so effective. This project bridges that gap.

Based on [Vercel's research](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) showing that **AGENTS.md outperforms skills** (100% vs 79% pass rate), we use an AGENTS.md-first design where core orchestration logic is always in context.

## Features

| Feature | Description |
|---------|-------------|
| 🧠 **AGENTS.md-First** | Core orchestration logic always in context, not retrieved on-demand |
| 🚀 **5 Execution Modes** | autopilot, ultrawork, plan, eco, review |
| 🔧 **8 Native Skills** | Git, Playwright, Debug, and more |
| 🤖 **Multi-Agent** | PM + specialized agents via Codex MCP + Agents SDK |
| 📊 **Smart Routing** | Automatic model selection based on task complexity |
| 💾 **Session Management** | Pause, resume, and track long-running tasks |
| ⚡ **CLI Wrapper** | `omc` command with keyword detection |

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/siltarre/oh-my-codex.git
cd oh-my-codex

# Run installer
./install.sh
```

The installer will:
- Install skills to `~/.codex/skills/`
- Copy config to `~/.codex/config.toml`
- Install `omc` CLI to `~/.local/bin/`
- Optionally install Python orchestrator

### Basic Usage

```bash
# Autopilot mode — full autonomous execution
omc "autopilot: build a REST API for task management"

# Ultrawork mode — parallel multi-file operations
omc "ulw: rename all 'userId' to 'user_id' across the codebase"

# Plan mode — interview and design (no execution)
omc "plan: design the payment system architecture"

# Eco mode — token-efficient, quick tasks
omc "eco: add .env to gitignore"

# Direct pass-through (no keyword = direct Codex)
omc "fix the bug in auth.py"
```

## Execution Modes

### Autopilot (`autopilot:`)

Full autonomous execution. The agent will:
1. Analyze the task and create a detailed plan
2. Execute each step independently
3. Verify results against acceptance criteria
4. Iterate until complete (or ask for help)

**Best for:** Feature development, complex implementations, multi-step tasks

```bash
omc "autopilot: implement user authentication with JWT, including login, logout, and token refresh"
```

### Ultrawork (`ulw:`)

Parallel execution for large-scale operations. Decomposes work into independent units and processes them concurrently.

**Best for:** Refactoring, bulk updates, codebase-wide changes

```bash
omc "ulw: add TypeScript types to all utility functions in src/utils/"
```

### Plan (`plan:`)

Interview-driven planning without execution. Asks clarifying questions, then generates a comprehensive plan document.

**Best for:** Architecture design, project kickoff, complex requirements

```bash
omc "plan: design a real-time collaborative document editor"
```

### Eco (`eco:`)

Token-efficient mode for simple tasks. Minimal output, direct action, fast completion.

**Best for:** Quick fixes, simple changes, routine operations

```bash
omc "eco: update the version to 2.0.0 in package.json"
```

### Ralph (`ralph:`)

Persistent autopilot that never gives up. Keeps trying until the task is truly complete.

**Best for:** Stubborn bugs, complex debugging, tasks that need persistence

```bash
omc "ralph: fix all TypeScript errors in the project"
```

## Skills

Skills are specialized instruction sets that Codex loads on-demand. Oh My Codex includes 8 built-in skills:

| Skill | Description | Trigger |
|-------|-------------|---------|
| **autopilot** | Autonomous feature development | `autopilot:` keyword |
| **ultrawork** | Parallel multi-file operations | `ulw:` keyword |
| **planner** | Interview-driven planning | `plan:` keyword |
| **eco** | Token-efficient execution | `eco:` keyword |
| **reviewer** | Code review with security/perf checklists | Auto on PR/review |
| **git-master** | Git workflow (rebase, cherry-pick, etc.) | Git-related tasks |
| **playwright** | E2E testing and browser automation | Testing tasks |
| **debug** | Systematic debugging methodology | Debugging tasks |

### Installing External Skills

```bash
# From skills.sh registry
npx skills add supabase/supabase-postgres-best-practices

# Skills are installed to ~/.codex/skills/
```

## Multi-Agent Orchestration

When using complex modes (autopilot, ultrawork), Oh My Codex can spawn specialized agents:

```
┌─────────────────────────────────────────────────────────┐
│                   Project Manager                        │
│            (orchestrates, delegates, verifies)           │
└─────────────────────┬───────────────────────────────────┘
                      │
       ┌──────────────┼──────────────┬──────────────┐
       ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Frontend   │ │  Backend    │ │  QA Tester  │ │  Reviewer   │
│  Developer  │ │  Developer  │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
     React         APIs           Tests          Security
     TypeScript    Databases      Edge cases     Performance
     CSS           Auth           Coverage       Quality
```

**Requirements:** `pip install oh-my-codex[full]`

Each agent has specialized instructions and can use Codex CLI tools via MCP.

## Architecture

```
oh-my-codex/
├── AGENTS.md                 # 🧠 Core orchestration brain
│                             #    Always loaded, contains routing logic
├── .codex/skills/            # 🔧 Native Codex skills
│   ├── autopilot/            #    Full autonomous mode
│   ├── ultrawork/            #    Parallel execution
│   ├── planner/              #    Interview & planning
│   ├── eco/                  #    Token-efficient
│   ├── reviewer/             #    Code review + references/
│   ├── git-master/           #    Git workflows
│   ├── playwright/           #    E2E testing
│   └── debug/                #    Systematic debugging
│
├── orchestrator/             # 🤖 Python multi-agent system
│   ├── main.py               #    Orchestrator entry point
│   ├── agents/               #    Agent definitions (PM, Frontend, etc.)
│   │   └── base.py           #    Agent configs and instructions
│   ├── session.py            #    Session persistence
│   ├── mcp.py                #    MCP server configurations
│   ├── router.py             #    Task classification & model routing
│   ├── utils.py              #    Helper utilities
│   └── cli.py                #    CLI entry point
│
├── bin/omc                   # ⚡ CLI wrapper script
├── config.toml               # ⚙️ Codex configuration
├── pyproject.toml            # 📦 Python package definition
└── install.sh                # 🚀 One-click installer
```

## Configuration

### ~/.codex/config.toml

```toml
[model]
default = "o3"

# Model routing by complexity
[model.routing]
simple = "gpt-4.1-mini"    # Trivial tasks, eco mode
standard = "gpt-4.1"       # Normal tasks
complex = "o3"             # Architecture, multi-agent

[skills]
auto_load = true           # Auto-load matching skills

[compaction]
enabled = true             # Enable for long sessions
threshold_tokens = 100000
```

### MCP Server Configuration

```toml
[mcp.github]
command = "npx"
args = ["-y", "@anthropic/mcp-server-github"]
env = { GITHUB_TOKEN = "your-token" }

[mcp.postgres]
command = "npx"
args = ["-y", "@anthropic/mcp-server-postgres", "postgresql://..."]
```

## CLI Reference

```bash
# Execute with mode detection
omc "autopilot: build feature X"

# Force specific mode
omc -m ultrawork "refactor utils"

# Specify model
omc --model gpt-4.1 "simple task"

# Session management
omc --list                    # List all sessions
omc --resume <session-id>     # Resume paused session

# Status and diagnostics
omc --status                  # Check installation status

# Direct Codex (skip orchestration)
omc --direct "quick fix"

# Verbose output
omc -v "autopilot: complex task"
```

## Design Philosophy

### Why AGENTS.md-First?

Vercel's research found that agents using AGENTS.md with compressed document indices achieved **100% task completion**, while skills-based retrieval only hit **79%** even with explicit instructions.

Key insight: **Information always in context beats on-demand retrieval.**

The agent doesn't have to decide whether to look something up — the information is always there.

### Skill Routing Best Practices

From [OpenAI's guidance](https://developers.openai.com/blog/skills-shell-tips):

1. **Write descriptions like routing logic**, not marketing copy
2. **Include "Don't use when"** sections to prevent misuse
3. **Add negative examples** to reduce false triggers
4. **Put templates inside skills** — they only load when needed

## Session Management

Oh My Codex tracks long-running tasks:

```bash
# Sessions are auto-created for complex tasks
omc "autopilot: build authentication system"
# → Session: 20260213_143022_a1b2c3d4

# List sessions
omc --list
# ID                          Status      Mode        Task
# 20260213_143022_a1b2c3d4    active      autopilot   build authentication...

# Resume if interrupted
omc --resume 20260213_143022_a1b2c3d4
```

Sessions are stored in `~/.codex/sessions/` as JSON.

## Troubleshooting

### `omc: command not found`

Add `~/.local/bin` to your PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add to your `~/.zshrc` or `~/.bashrc`.

### Multi-agent not working

Install the full package:

```bash
pip install -e ".[full]"
```

### Skills not loading

Check installation:

```bash
omc --status
ls ~/.codex/skills/
```

## Roadmap

- [x] Phase 1: Skills + AGENTS.md core
- [x] Phase 2: Python orchestrator with Agents SDK
- [x] Phase 3: Model routing & task classification
- [x] Phase 4: CLI wrapper (`omc`) + session management
- [ ] Phase 5: Native Codex plugin (waiting for Codex plugin system)

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Credits

- [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) — Original inspiration
- [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) — Architecture reference
- [Supabase Agent Skills](https://github.com/supabase/agent-skills) — Skill structure standard
- [Vercel AGENTS.md Research](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) — Design philosophy

## License

MIT © 2026 tarae
