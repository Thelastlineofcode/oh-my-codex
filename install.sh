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
BLUE='\033[0;34m'
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

# ============================================
# Billing Provider Setup
# ============================================
echo -e "${BLUE}💳 Billing Setup${NC}"
echo ""
echo "How do you want to use Codex?"
echo ""
echo "  1) ${GREEN}Codex Pro${NC} - \$200/month subscription (unlimited usage)"
echo "  2) ${YELLOW}OpenAI API${NC} - Pay per token (usage-based)"
echo ""
read -p "Select [1/2]: " -n 1 -r BILLING_CHOICE
echo ""

case $BILLING_CHOICE in
    1)
        PROVIDER="codex"
        echo -e "   → Using ${GREEN}Codex Pro${NC} subscription"
        ;;
    2)
        PROVIDER="openai"
        echo -e "   → Using ${YELLOW}OpenAI API${NC} billing"
        ;;
    *)
        PROVIDER="codex"
        echo -e "   → Defaulting to ${GREEN}Codex Pro${NC}"
        ;;
esac
echo ""

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

# Install config with provider setting
echo -e "${GREEN}⚙️  Installing config.toml...${NC}"
if [ -f "$CODEX_DIR/config.toml" ]; then
    echo -e "${YELLOW}   Backing up existing config to config.toml.bak${NC}"
    cp "$CODEX_DIR/config.toml" "$CODEX_DIR/config.toml.bak"
fi

# Copy and inject provider setting
cp "$REPO_DIR/config.toml" "$CODEX_DIR/config.toml"

# Add billing section if not exists
if ! grep -q "\[billing\]" "$CODEX_DIR/config.toml"; then
    cat >> "$CODEX_DIR/config.toml" << EOF

[billing]
# Provider: "codex" (subscription) or "openai" (API)
provider = "$PROVIDER"
EOF
else
    # Update existing provider setting
    sed -i.tmp "s/^provider = .*/provider = \"$PROVIDER\"/" "$CODEX_DIR/config.toml"
    rm -f "$CODEX_DIR/config.toml.tmp"
fi
echo "   → Provider set to: $PROVIDER"

# Install CLI wrapper
echo -e "${GREEN}🔧 Installing omx CLI...${NC}"
cp "$REPO_DIR/bin/omx" "$BIN_DIR/omx"
chmod +x "$BIN_DIR/omx"

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
echo "  omx \"autopilot: build a REST API\"     # Full orchestration"
echo "  omx \"ulw: refactor all files\"         # Parallel execution"
echo "  omx \"plan: design the system\"         # Planning mode"
echo "  omx \"eco: quick fix\"                  # Token-efficient"
echo "  omx --status                           # Check status"
echo "  omx --list                             # List sessions"
echo ""
echo "Skills installed to: $SKILLS_DIR"
echo "Config at: $CODEX_DIR/config.toml"
echo ""
