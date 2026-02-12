"""
Constants for Oh My Codex.
Centralized configuration values used across modules.
"""

from typing import Dict, List

# Session management
SESSION_ID_UNIQUE_LENGTH = 8
SESSION_LIST_LIMIT = 15
SESSION_CLEANUP_DAYS = 30

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
MODEL_NANO = "gpt-5-nano"           # Fastest, cheapest
MODEL_MINI = "gpt-5-mini"           # Fast, cheap  
MODEL_STANDARD = "gpt-5.1-codex"    # Balanced (Codex optimized)
MODEL_POWERFUL = "gpt-5.2-codex"    # Most capable
MODEL_MAX = "gpt-5.1-codex-max"     # Long-running tasks

# Legacy aliases
MODEL_FAST = MODEL_MINI

# Reasoning effort levels (for GPT-5.1+)
REASONING_NONE = "none"
REASONING_LOW = "low"
REASONING_MEDIUM = "medium"
REASONING_HIGH = "high"
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
    "autopilot": REASONING_MEDIUM,
    "ultrawork": REASONING_LOW,
    "team": REASONING_MEDIUM,
    "ultrapilot": REASONING_HIGH,
    "ralph": REASONING_HIGH,
    "pipeline": REASONING_LOW,
    "ralplan": REASONING_HIGH,
    "research": REASONING_HIGH,
    "deepsearch": REASONING_LOW,
    "debug": REASONING_HIGH,
}
