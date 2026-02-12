# Doctor Skill

Diagnose and fix Oh My Codex installation issues.

## When to Use
- Installation problems
- Configuration errors
- Skill loading failures
- Performance issues
- After updates

## Diagnostic Checks

### Environment
```
□ Node.js version (>= 18)
□ Python version (>= 3.10)
□ Codex CLI installed
□ PATH configured correctly
□ Required permissions
```

### Installation
```
□ Skills directory exists
□ All skills have SKILL.md
□ Config file valid
□ No conflicting configs
□ Dependencies installed
```

### Configuration
```
□ config.toml syntax valid
□ Model names correct
□ MCP servers configured
□ API keys present (if needed)
□ Profiles defined
```

### Runtime
```
□ Can spawn agents
□ MCP servers reachable
□ Sessions directory writable
□ No zombie processes
□ Memory usage normal
```

## Common Issues

### "omc: command not found"
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify
which omc
```

### "Skill not loading"
```bash
# Check skill exists
ls ~/.codex/skills/

# Verify SKILL.md present
cat ~/.codex/skills/autopilot/SKILL.md
```

### "MCP connection failed"
```bash
# Test MCP server
npx -y codex mcp

# Check config
cat ~/.codex/config.toml | grep mcp
```

### "Agent SDK not available"
```bash
# Install full package
pip install oh-my-codex[full]

# Or install SDK directly
pip install openai-agents-sdk
```

## Repair Actions

### Reset Configuration
```bash
# Backup current
cp ~/.codex/config.toml ~/.codex/config.toml.bak

# Reset to default
omx --reset-config
```

### Reinstall Skills
```bash
# Remove and reinstall
rm -rf ~/.codex/skills
./install.sh
```

### Clear Cache
```bash
# Clear sessions
rm -rf ~/.codex/sessions/*

# Clear errors
rm -rf ~/.codex/errors/*
```

## Usage

```
doctor: check my Oh My Codex installation

doctor: why aren't skills loading

doctor: diagnose slow performance
```

## Output Format

```markdown
## Oh My Codex Health Check

### Environment
✅ Node.js: v22.12.0
✅ Python: 3.12.0
✅ Codex CLI: 1.2.3
⚠️ PATH: ~/.local/bin not in PATH

### Installation
✅ Skills directory: ~/.codex/skills
✅ Skills installed: 20
✅ Config: Valid

### Runtime
✅ Agent SDK: Available
❌ MCP GitHub: Connection failed
✅ Sessions: Writable

### Issues Found
1. **PATH Configuration**
   - ~/.local/bin not in PATH
   - Fix: Add to ~/.zshrc

2. **MCP GitHub**
   - Connection refused
   - Fix: Check GITHUB_TOKEN

### Recommended Actions
1. Run: export PATH="$HOME/.local/bin:$PATH"
2. Set GITHUB_TOKEN environment variable
```
