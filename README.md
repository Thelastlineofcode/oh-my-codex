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

Inspired by [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode), adapted for OpenAI Codex CLI.

## Why Oh My Codex?

OpenAI Codex CLI is powerful, but lacks the multi-agent orchestration that makes Claude Code + oh-my-claudecode so effective. This project bridges that gap.

Based on [Vercel's research](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) showing **AGENTS.md outperforms skills** (100% vs 79%), we use an AGENTS.md-first design.

## Features

| Feature | Description |
|---------|-------------|
| 🧠 **AGENTS.md-First** | Core orchestration always in context |
| 🚀 **8 Execution Modes** | team, autopilot, ultrawork, ralph, pipeline, eco, plan, ultrapilot |
| 🔧 **31 Native Skills** | Full toolkit matching oh-my-claudecode |
| 🤖 **32 Specialized Agents** | From PM to Data Scientist |
| 📊 **Smart Routing** | Automatic model selection |
| 💾 **Session Management** | Pause, resume, track |
| 📡 **HUD & Tracing** | Real-time metrics and debugging |

## Quick Start

```bash
# Clone
git clone https://github.com/junghwaYang/oh-my-codex.git
cd oh-my-codex

# Install
./install.sh

# Use
omc "autopilot: build a REST API for tasks"
```

## Execution Modes

| Mode | Keyword | Description |
|------|---------|-------------|
| **Team** | `team:` | Canonical multi-agent pipeline (plan→exec→verify→fix) |
| **Autopilot** | `autopilot:` | Full autonomous execution |
| **Ultrawork** | `ulw:` | Parallel multi-file operations |
| **Ralph** | `ralph:` | Persistent mode (never gives up) |
| **Ultrapilot** | `ultrapilot:` | Maximum parallelism |
| **Pipeline** | `pipeline:` | Sequential staged processing |
| **Eco** | `eco:` | Token-efficient execution |
| **Plan** | `plan:` | Interview-driven planning |

### Examples

```bash
# Team orchestration (recommended for complex tasks)
omc "team: build a fullstack app with auth"

# Autopilot for feature development
omc "autopilot: implement user dashboard"

# Parallel refactoring
omc "ulw: rename userId to user_id everywhere"

# Persistent debugging
omc "ralph: fix all TypeScript errors"

# Token-efficient quick fix
omc "eco: add .env to gitignore"

# Planning without execution
omc "plan: design the payment system"
```

## Skills (31)

### Orchestration
| Skill | Description |
|-------|-------------|
| `team` | Multi-agent staged pipeline |
| `autopilot` | Autonomous execution |
| `ultrawork` | Parallel execution |
| `ultrapilot` | Maximum parallelism |
| `ralph` | Persistent mode |
| `pipeline` | Sequential processing |
| `swarm` | Legacy multi-agent (→ team) |

### Planning & Analysis
| Skill | Description |
|-------|-------------|
| `planner` | Interview-driven planning |
| `ralplan` | Iterative planning consensus |
| `analyze` | Code quality analysis |
| `research` | Deep research |
| `deepsearch` | Codebase exploration |

### Development
| Skill | Description |
|-------|-------------|
| `eco` | Token-efficient mode |
| `tdd` | Test-driven development |
| `build-fix` | Fix build errors |
| `deepinit` | Project initialization |
| `release` | Version & changelog |

### Quality & Review
| Skill | Description |
|-------|-------------|
| `reviewer` | Code review |
| `code-review` | Comprehensive review |
| `security-review` | Security audit |
| `ultraqa` | Parallel testing |

### Tools & Utilities
| Skill | Description |
|-------|-------------|
| `git-master` | Git workflows |
| `playwright` | E2E testing |
| `debug` | Systematic debugging |
| `mcp-setup` | MCP configuration |
| `configure-notifications` | Alerts setup |

### System
| Skill | Description |
|-------|-------------|
| `doctor` | Installation diagnostics |
| `hud` | Real-time metrics |
| `trace` | Execution tracing |
| `learner` | Pattern extraction |
| `note` | Session notes |

## Agents (32)

### Primary Orchestration
- **PM** — Master orchestrator
- **Coordinator** — Parallel execution management
- **Executor** — Task execution
- **Deep Executor** — Complex implementations

### Planning & Analysis
- **Planner** — Creates actionable plans
- **Analyst** — System analysis
- **Researcher** — Information gathering
- **Explorer** — Codebase navigation

### Architecture & Design
- **Architect** — System design
- **Designer** — UI/UX design
- **System Designer** — Distributed systems

### Development
- **Frontend** — React, Vue, TypeScript
- **Backend** — APIs, databases
- **Fullstack** — End-to-end development
- **Mobile** — React Native, Flutter
- **DevOps** — CI/CD, infrastructure

### Quality & Testing
- **Tester** — Unit/integration tests
- **QA** — Quality assurance
- **Security** — Security engineering
- **Performance** — Performance optimization

### Review & Critique
- **Reviewer** — Code review
- **Critic** — Challenge assumptions

### Specialized
- **Scientist** — Data science
- **Data** — Data engineering
- **ML** — Machine learning
- **Writer** — Documentation
- **Docs** — API documentation
- **Vision** — Visual analysis

### Support
- **Debugger** — Bug finding
- **Refactorer** — Code improvement
- **Migrator** — Upgrades & migrations

## Architecture

```
oh-my-codex/
├── AGENTS.md                 # Core orchestration brain
├── .codex/skills/            # 31 native skills
│   ├── team/
│   ├── autopilot/
│   ├── ultrawork/
│   └── ... (28 more)
├── orchestrator/             # Python multi-agent
│   ├── agents/               # 32 agent definitions
│   ├── session.py            # Session management
│   ├── mcp.py                # MCP servers
│   ├── router.py             # Model routing
│   └── cli.py                # CLI entry
├── bin/omc                   # CLI wrapper
├── config.toml               # Configuration
└── install.sh                # Installer
```

## CLI Reference

```bash
omc "task description"          # Auto-detect mode
omc "autopilot: task"           # Explicit mode
omc -m ultrawork "task"         # Force mode
omc --model gpt-4.1 "task"      # Model override
omc --list                      # List sessions
omc --resume <id>               # Resume session
omc --status                    # Check status
omc -v "task"                   # Verbose
```

## Configuration

### ~/.codex/config.toml

```toml
[model]
default = "o3"

[model.routing]
simple = "gpt-4.1-mini"
standard = "gpt-4.1"
complex = "o3"

[hud]
enabled = true
style = "standard"

[trace]
enabled = false
level = "standard"
```

## Credits

- [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) — Original inspiration
- [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) — Architecture reference
- [Supabase Agent Skills](https://github.com/supabase/agent-skills) — Skill structure
- [Vercel Research](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) — Design philosophy

## License

MIT
