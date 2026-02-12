#!/bin/bash
# Oh My Codex Installer
# Installs skills, config, and optionally the Python package

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
CODEX_DIR="$HOME/.codex"
SKILLS_DIR="$CODEX_DIR/skills"
BIN_DIR="$HOME/.local/bin"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Installing Oh My Codex...${NC}"
echo ""

# Create directories
mkdir -p "$SKILLS_DIR"
mkdir -p "$CODEX_DIR/plans"
mkdir -p "$CODEX_DIR/sessions"
mkdir -p "$CODEX_DIR/errors"
mkdir -p "$BIN_DIR"

# Install skills
echo -e "${GREEN}📦 Installing skills...${NC}"
for skill in "$REPO_DIR/.codex/skills"/*; do
    if [ -d "$skill" ]; then
        skill_name=$(basename "$skill")
        echo "   → $skill_name"
        rm -rf "$SKILLS_DIR/$skill_name"
        cp -r "$skill" "$SKILLS_DIR/"
    fi
done

# Install config
if [ ! -f "$CODEX_DIR/config.toml" ]; then
    echo -e "${GREEN}⚙️  Installing config.toml...${NC}"
    cp "$REPO_DIR/config.toml" "$CODEX_DIR/config.toml"
else
    echo -e "${YELLOW}⚙️  config.toml exists, skipping (backup: config.toml.omc)${NC}"
    cp "$REPO_DIR/config.toml" "$CODEX_DIR/config.toml.omc"
fi

# Install CLI wrapper
echo -e "${GREEN}🔧 Installing omc CLI...${NC}"
cp "$REPO_DIR/bin/omc" "$BIN_DIR/omc"
chmod +x "$BIN_DIR/omc"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo -e "${YELLOW}⚠️  Add ~/.local/bin to your PATH:${NC}"
    echo '   export PATH="$HOME/.local/bin:$PATH"'
fi

# Optional: Install Python package
echo ""
read -p "📦 Install Python orchestrator (enables multi-agent)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Installing Python package...${NC}"
    
    # Check for pip
    if command -v pip3 &> /dev/null; then
        PIP="pip3"
    elif command -v pip &> /dev/null; then
        PIP="pip"
    else
        echo -e "${RED}❌ pip not found${NC}"
        exit 1
    fi
    
    # Install with full dependencies
    cd "$REPO_DIR"
    $PIP install -e ".[full]" || $PIP install -e .
fi

# Optional: Copy AGENTS.md
echo ""
read -p "📝 Copy AGENTS.md to current directory? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "./AGENTS.md" ]; then
        echo -e "${YELLOW}   AGENTS.md exists, backing up to AGENTS.md.bak${NC}"
        mv ./AGENTS.md ./AGENTS.md.bak
    fi
    cp "$REPO_DIR/AGENTS.md" ./AGENTS.md
    echo "   → AGENTS.md copied"
fi

echo ""
echo -e "${GREEN}✅ Oh My Codex installed!${NC}"
echo ""
echo "Usage:"
echo "  omc \"autopilot: build a REST API\"     # Full orchestration"
echo "  omc \"ulw: refactor all files\"         # Parallel execution"
echo "  omc \"plan: design the system\"         # Planning mode"
echo "  omc \"eco: quick fix\"                  # Token-efficient"
echo "  omc --status                           # Check status"
echo "  omc --list                             # List sessions"
echo ""
echo "Skills installed to: $SKILLS_DIR"
echo "Config at: $CODEX_DIR/config.toml"
echo ""
