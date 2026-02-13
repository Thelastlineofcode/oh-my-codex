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

# Arrow key selection function
select_option() {
    local options=("$@")
    local selected=0
    local key
    
    # Hide cursor
    tput civis
    
    # Print options
    print_options() {
        for i in "${!options[@]}"; do
            tput cuu1 2>/dev/null || true
        done
        tput el 2>/dev/null || true
        
        for i in "${!options[@]}"; do
            tput el 2>/dev/null || true
            if [ $i -eq $selected ]; then
                echo -e "  ${GREEN}▸ ${options[$i]}${NC}"
            else
                echo -e "    ${options[$i]}"
            fi
        done
    }
    
    # Initial print
    for opt in "${options[@]}"; do
        echo ""
    done
    print_options
    
    # Read keys
    while true; do
        read -rsn1 key
        case "$key" in
            $'\x1b')  # ESC sequence
                read -rsn2 key
                case "$key" in
                    '[A')  # Up arrow
                        ((selected > 0)) && ((selected--))
                        ;;
                    '[B')  # Down arrow
                        ((selected < ${#options[@]} - 1)) && ((selected++))
                        ;;
                esac
                print_options
                ;;
            '')  # Enter
                break
                ;;
        esac
    done
    
    # Show cursor
    tput cnorm
    
    return $selected
}

echo -e "${BLUE}💳 Billing Setup${NC}"
echo ""
echo "How do you want to use Codex?"
echo -e "${YELLOW}(Use ↑↓ arrows to select, Enter to confirm)${NC}"

select_option \
    "${GREEN}Codex Pro${NC} - \$200/month subscription (unlimited usage)" \
    "${YELLOW}OpenAI API${NC} - Pay per token (usage-based)"
BILLING_CHOICE=$?

case $BILLING_CHOICE in
    0)
        PROVIDER="codex"
        echo ""
        echo -e "   → Using ${GREEN}Codex Pro${NC} subscription"
        ;;
    1)
        PROVIDER="openai"
        echo ""
        echo -e "   → Using ${YELLOW}OpenAI API${NC} billing"
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

# Install Codex CLI config (YAML format)
echo -e "${GREEN}⚙️  Installing config.yaml...${NC}"
if [ -f "$CODEX_DIR/config.yaml" ]; then
    echo -e "${YELLOW}   Backing up existing config to config.yaml.bak${NC}"
    cp "$CODEX_DIR/config.yaml" "$CODEX_DIR/config.yaml.bak"
fi

# Remove old TOML config if exists (causes errors)
if [ -f "$CODEX_DIR/config.toml" ]; then
    echo -e "${YELLOW}   Removing old config.toml (incompatible format)${NC}"
    mv "$CODEX_DIR/config.toml" "$CODEX_DIR/config.toml.old"
fi

# Create Codex CLI config
cat > "$CODEX_DIR/config.yaml" << EOF
# Oh My Codex - Codex CLI Configuration
model: o4-mini
approvalMode: suggest
fullAutoErrorMode: ask-user
notify: true

history:
  maxSize: 1000
  saveHistory: true
  sensitivePatterns: []
EOF

# Create OMX orchestrator config (separate file)
cat > "$CODEX_DIR/omx-config.yaml" << EOF
# Oh My Codex Orchestrator Settings
billing:
  provider: $PROVIDER

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
    eco: none
    plan: medium
    autopilot: high
    ultrawork: medium
    ultrapilot: xhigh
    ralph: xhigh
    review: high
    debug: xhigh
EOF
echo "   → Codex CLI config: config.yaml"
echo "   → OMX orchestrator config: omx-config.yaml"
echo "   → Billing provider: $PROVIDER"

# Codex Pro login prompt
if [ "$PROVIDER" = "codex" ]; then
    echo ""
    echo -e "${BLUE}🔐 Codex Pro Authentication${NC}"
    echo -e "${YELLOW}(Use ↑↓ arrows to select, Enter to confirm)${NC}"
    
    select_option "Login now" "Skip (login later with 'codex login')"
    LOGIN_CHOICE=$?
    
    if [ $LOGIN_CHOICE -eq 0 ]; then
        echo ""
        if command -v codex &> /dev/null; then
            echo -e "   Opening browser for Codex login..."
            codex login || echo -e "${YELLOW}   ⚠️ Login skipped - run 'codex login' later${NC}"
        else
            echo -e "${YELLOW}   ⚠️ Codex CLI not installed yet${NC}"
            echo -e "   Run: ${GREEN}npm i -g @openai/codex${NC}"
            echo -e "   Then: ${GREEN}codex login${NC}"
        fi
    else
        echo ""
        echo -e "   → Run ${GREEN}codex login${NC} when ready"
    fi
fi

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
echo -e "📦 Install Python orchestrator? ${YELLOW}(enables multi-agent)${NC}"
echo -e "${YELLOW}(Use ↑↓ arrows to select, Enter to confirm)${NC}"

select_option "Yes - Install full orchestrator" "No - Skip"
INSTALL_PY=$?

if [ $INSTALL_PY -eq 0 ]; then
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
echo -e "📝 Copy AGENTS.md to current directory?"
echo -e "${YELLOW}(Use ↑↓ arrows to select, Enter to confirm)${NC}"

select_option "Yes - Copy AGENTS.md" "No - Skip"
COPY_AGENTS=$?

if [ $COPY_AGENTS -eq 0 ]; then
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
