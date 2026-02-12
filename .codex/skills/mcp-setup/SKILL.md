# MCP Setup Skill

Configure Model Context Protocol servers.

## What is MCP?

MCP (Model Context Protocol) allows Codex to connect to external tools and data sources:
- File systems
- Databases
- APIs
- Custom tools

## Available Servers

### Core Servers

| Server | Purpose | Install |
|--------|---------|---------|
| filesystem | File operations | `@anthropic/mcp-server-filesystem` |
| github | GitHub API | `@anthropic/mcp-server-github` |
| postgres | PostgreSQL | `@anthropic/mcp-server-postgres` |
| sqlite | SQLite | `@anthropic/mcp-server-sqlite` |

### Extended Servers

| Server | Purpose | Install |
|--------|---------|---------|
| brave-search | Web search | `@anthropic/mcp-server-brave-search` |
| memory | Persistent memory | `@anthropic/mcp-server-memory` |
| puppeteer | Browser automation | `@anthropic/mcp-server-puppeteer` |
| slack | Slack integration | `@anthropic/mcp-server-slack` |

## Configuration

### ~/.codex/config.toml

```toml
[mcp.filesystem]
command = "npx"
args = ["-y", "@anthropic/mcp-server-filesystem", "/path/to/allowed"]

[mcp.github]
command = "npx"
args = ["-y", "@anthropic/mcp-server-github"]
env = { GITHUB_TOKEN = "ghp_xxx" }

[mcp.postgres]
command = "npx"
args = ["-y", "@anthropic/mcp-server-postgres", "postgresql://user:pass@localhost/db"]

[mcp.brave]
command = "npx"
args = ["-y", "@anthropic/mcp-server-brave-search"]
env = { BRAVE_API_KEY = "xxx" }
```

## Setup Commands

```bash
# Test MCP server
npx -y @anthropic/mcp-server-filesystem /tmp

# Verify configuration
omx --status
```

## Usage

```
mcp-setup: configure GitHub integration

mcp-setup: add PostgreSQL database connection

mcp-setup: enable web search with Brave
```

## Security Notes

1. **Limit filesystem access** - Only allow necessary directories
2. **Use environment variables** - Don't hardcode secrets
3. **Rotate tokens** - Regular credential rotation
4. **Audit access** - Review what MCP servers can do

## Troubleshooting

### "MCP server not found"
```bash
# Install the server
npm install -g @anthropic/mcp-server-github
```

### "Connection refused"
```bash
# Check server is running
npx -y @anthropic/mcp-server-github
```

### "Permission denied"
```bash
# Check token/credentials
echo $GITHUB_TOKEN
```
