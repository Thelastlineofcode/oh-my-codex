"""
Constants for Oh My Codex.
Centralized configuration values used across modules.
"""

from typing import Dict, List

# Session management
SESSION_ID_UNIQUE_LENGTH = 8
SESSION_LIST_LIMIT = 15
SESSION_CLEANUP_DAYS = 30

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

# Model tiers
MODEL_FAST = "gpt-4.1-mini"
MODEL_STANDARD = "gpt-4.1"
MODEL_POWERFUL = "o3"

# Mode to model mapping
MODE_MODEL_MAP: Dict[str, str] = {
    "eco": MODEL_FAST,
    "plan": MODEL_STANDARD,
    "tdd": MODEL_STANDARD,
    "review": MODEL_POWERFUL,
    "autopilot": MODEL_POWERFUL,
    "ultrawork": MODEL_POWERFUL,
    "team": MODEL_POWERFUL,
    "ultrapilot": MODEL_POWERFUL,
    "ralph": MODEL_POWERFUL,
    "pipeline": MODEL_STANDARD,
    "ralplan": MODEL_POWERFUL,
    "research": MODEL_STANDARD,
    "deepsearch": MODEL_FAST,
    "debug": MODEL_POWERFUL,
}
