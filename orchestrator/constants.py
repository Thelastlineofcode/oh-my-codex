"""
Constants for Oh My Codex.
Centralized configuration values used across modules.
"""

from typing import Dict, List

# Session management
SESSION_ID_UNIQUE_LENGTH = 8
SESSION_LIST_LIMIT = 15
SESSION_CLEANUP_DAYS = 30

# State management
STATE_DB_FILENAME = "omx-state.db"
STATE_CLEANUP_DAYS = 30

# Verification
VERIFY_MAX_RETRIES = 3
VERIFY_SKIP_MODES = {"plan", "eco", "research", "deepsearch"}

# HUD
HUD_DEFAULT_PRESET = "focused"
HUD_WATCH_INTERVAL = 2.0  # seconds

# Billing providers
PROVIDER_CODEX = "codex"      # Subscription model ($200/month)
PROVIDER_OPENAI = "openai"    # API billing (pay per token)
DEFAULT_PROVIDER = PROVIDER_CODEX

# Keywords that trigger special execution modes
# Format: keyword -> mode
MODE_KEYWORDS: Dict[str, str] = {
    # Autopilot variants
    "autopilot:": "autopilot",
    "autopilot ": "autopilot",
    "auto:": "autopilot",
    
    # Ultrawork (parallel)
    "ulw:": "ultrawork",
    "ulw ": "ultrawork",
    "ultrawork:": "ultrawork",
    "ultrawork ": "ultrawork",
    
    # Team orchestration
    "team:": "team",
    "team ": "team",
    
    # Ultrapilot (max parallel)
    "ultrapilot:": "ultrapilot",
    "ultrapilot ": "ultrapilot",
    
    # Ralph (persistent)
    "ralph:": "ralph",
    "ralph ": "ralph",
    
    # Pipeline (sequential)
    "pipeline:": "pipeline",
    "pipeline ": "pipeline",
    
    # Planning
    "plan:": "plan",
    "plan ": "plan",
    "ralplan:": "ralplan",
    "ralplan ": "ralplan",
    
    # Eco (token-efficient)
    "eco:": "eco",
    "eco ": "eco",
    
    # Development
    "tdd:": "tdd",
    "tdd ": "tdd",
    
    # Review
    "review:": "review",
    "review ": "review",
    "code-review:": "review",
    
    # Research
    "research:": "research",
    "research ": "research",
    "deepsearch:": "deepsearch",
    "deepsearch ": "deepsearch",
    
    # Debug
    "debug:": "debug",
    "debug ": "debug",
}

# Modes that require full orchestration vs direct Codex
ORCHESTRATED_MODES: List[str] = [
    "autopilot",
    "ultrawork",
    "team",
    "ultrapilot",
    "ralph",
    "pipeline",
    "ralplan",
]

# Modes that can use direct Codex with minimal overhead
DIRECT_MODES: List[str] = [
    "eco",
    "plan",
    "tdd",
    "review",
    "research",
    "deepsearch",
    "debug",
]

# Model tiers (2026-02 latest)
MODEL_SPARK = "gpt-5.3-codex-spark" # Real-time, 1000+ tok/s
MODEL_MINI = "gpt-5-codex-mini"     # Cost-effective
MODEL_STANDARD = "gpt-5.2-codex"    # Balanced
MODEL_POWERFUL = "gpt-5.3-codex"    # Most capable
MODEL_MAX = "gpt-5.1-codex-max"     # Long-running tasks

# Legacy aliases
MODEL_FAST = MODEL_SPARK
MODEL_NANO = MODEL_MINI

# Reasoning effort levels (for GPT-5.1+)
REASONING_NONE = "none"
REASONING_LOW = "low"
REASONING_MEDIUM = "medium"
REASONING_HIGH = "high"
REASONING_XHIGH = "xhigh"  # GPT-5.3-codex
DEFAULT_REASONING = REASONING_NONE

# Mode to model mapping
MODE_MODEL_MAP: Dict[str, str] = {
    "eco": MODEL_MINI,
    "plan": MODEL_STANDARD,
    "tdd": MODEL_STANDARD,
    "review": MODEL_POWERFUL,
    "autopilot": MODEL_POWERFUL,
    "ultrawork": MODEL_POWERFUL,
    "team": MODEL_POWERFUL,
    "ultrapilot": MODEL_MAX,
    "ralph": MODEL_MAX,
    "pipeline": MODEL_STANDARD,
    "ralplan": MODEL_POWERFUL,
    "research": MODEL_STANDARD,
    "deepsearch": MODEL_MINI,
    "debug": MODEL_POWERFUL,
}

# Mode to reasoning effort mapping
MODE_REASONING_MAP: Dict[str, str] = {
    "eco": REASONING_NONE,
    "plan": REASONING_MEDIUM,
    "tdd": REASONING_LOW,
    "review": REASONING_HIGH,
    "autopilot": REASONING_HIGH,
    "ultrawork": REASONING_MEDIUM,
    "team": REASONING_HIGH,
    "ultrapilot": REASONING_XHIGH,  # Maximum reasoning
    "ralph": REASONING_XHIGH,       # Never give up = max thinking
    "pipeline": REASONING_LOW,
    "ralplan": REASONING_HIGH,
    "research": REASONING_HIGH,
    "deepsearch": REASONING_MEDIUM,
    "debug": REASONING_XHIGH,       # Deep debugging = max thinking
}
