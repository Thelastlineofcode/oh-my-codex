"""
Model routing and task classification for Oh My Codex.
"""

import re
from enum import Enum
from typing import Optional, Tuple
from dataclasses import dataclass


class TaskComplexity(Enum):
    TRIVIAL = "trivial"    # One-liner, typo fix
    SIMPLE = "simple"      # Single file, clear task
    MEDIUM = "medium"      # Multi-file, some complexity
    COMPLEX = "complex"    # Architecture, multi-component
    CRITICAL = "critical"  # Security, production, high-stakes


class ModelTier(Enum):
    FAST = "gpt-4.1-mini"
    STANDARD = "gpt-4.1"
    POWERFUL = "o3"


@dataclass
class RoutingDecision:
    model: str
    complexity: TaskComplexity
    mode: str
    confidence: float
    reason: str


# Patterns for task classification
COMPLEXITY_PATTERNS = {
    TaskComplexity.TRIVIAL: [
        r"typo",
        r"fix\s+spelling",
        r"rename\s+\w+\s+to\s+\w+",
        r"add\s+\w+\s+to\s+\.?gitignore",
        r"update\s+version",
        r"change\s+\w+\s+from\s+.+\s+to\s+.+",
    ],
    TaskComplexity.SIMPLE: [
        r"add\s+(a\s+)?function",
        r"create\s+(a\s+)?component",
        r"fix\s+(the\s+)?bug",
        r"update\s+(the\s+)?style",
        r"add\s+(a\s+)?test",
    ],
    TaskComplexity.MEDIUM: [
        r"refactor",
        r"implement\s+\w+\s+feature",
        r"add\s+authentication",
        r"create\s+(an?\s+)?api",
        r"migrate",
        r"integrate",
    ],
    TaskComplexity.COMPLEX: [
        r"architect",
        r"design\s+(the\s+)?system",
        r"build\s+(a\s+)?(complete|full|entire)",
        r"rewrite",
        r"scale",
        r"optimize\s+(the\s+)?performance",
    ],
    TaskComplexity.CRITICAL: [
        r"security",
        r"production",
        r"deploy",
        r"database\s+migration",
        r"breaking\s+change",
        r"payment",
        r"authentication",
    ],
}

# Mode keywords
MODE_KEYWORDS = {
    "autopilot": ["autopilot", "auto", "autonomous"],
    "ultrawork": ["ulw", "ultrawork", "parallel"],
    "plan": ["plan", "design", "architect"],
    "eco": ["eco", "quick", "fast", "simple"],
}


def classify_complexity(task: str) -> Tuple[TaskComplexity, float]:
    """
    Classify task complexity based on patterns.
    Returns (complexity, confidence).
    """
    task_lower = task.lower()
    
    # Check each complexity level
    matches = {}
    for complexity, patterns in COMPLEXITY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, task_lower):
                matches[complexity] = matches.get(complexity, 0) + 1
    
    if not matches:
        # Default to SIMPLE with low confidence
        return TaskComplexity.SIMPLE, 0.3
    
    # Return highest complexity with most matches
    best = max(matches.items(), key=lambda x: (x[0].value, x[1]))
    confidence = min(0.9, 0.5 + (best[1] * 0.2))
    return best[0], confidence


def detect_mode(task: str) -> Tuple[Optional[str], str]:
    """
    Detect execution mode from task keywords.
    Returns (mode, cleaned_task).
    """
    task_lower = task.lower()
    
    for mode, keywords in MODE_KEYWORDS.items():
        for keyword in keywords:
            # Check for keyword at start with colon or space
            patterns = [
                rf"^{keyword}:\s*",
                rf"^{keyword}\s+",
            ]
            for pattern in patterns:
                match = re.match(pattern, task_lower)
                if match:
                    return mode, task[match.end():].strip()
    
    return None, task


def select_model(complexity: TaskComplexity, mode: str = None) -> str:
    """
    Select appropriate model based on complexity and mode.
    """
    # Mode overrides
    if mode == "eco":
        return ModelTier.FAST.value
    
    # Complexity-based selection
    complexity_to_model = {
        TaskComplexity.TRIVIAL: ModelTier.FAST,
        TaskComplexity.SIMPLE: ModelTier.FAST,
        TaskComplexity.MEDIUM: ModelTier.STANDARD,
        TaskComplexity.COMPLEX: ModelTier.POWERFUL,
        TaskComplexity.CRITICAL: ModelTier.POWERFUL,
    }
    
    return complexity_to_model.get(complexity, ModelTier.STANDARD).value


def route_task(task: str) -> RoutingDecision:
    """
    Full routing decision for a task.
    """
    # Detect mode
    mode, clean_task = detect_mode(task)
    
    # Classify complexity
    complexity, confidence = classify_complexity(clean_task)
    
    # Select model
    model = select_model(complexity, mode)
    
    # Determine mode if not explicit
    if not mode:
        if complexity in [TaskComplexity.TRIVIAL, TaskComplexity.SIMPLE]:
            mode = "eco"
        elif complexity == TaskComplexity.COMPLEX:
            mode = "autopilot"
        else:
            mode = "autopilot"  # default
    
    # Generate reason
    reasons = []
    if mode:
        reasons.append(f"mode={mode}")
    reasons.append(f"complexity={complexity.value}")
    reasons.append(f"model={model}")
    
    return RoutingDecision(
        model=model,
        complexity=complexity,
        mode=mode,
        confidence=confidence,
        reason=", ".join(reasons),
    )


# Skill matching
SKILL_PATTERNS = {
    "git-master": [r"git\s", r"commit", r"branch", r"merge", r"rebase"],
    "playwright": [r"e2e", r"playwright", r"browser\s+test", r"automation"],
    "debug": [r"debug", r"troubleshoot", r"investigate", r"why\s+(is|does)"],
    "reviewer": [r"review", r"check\s+(the\s+)?code"],
    "autopilot": [r"build", r"create", r"implement"],
    "planner": [r"plan", r"design", r"architect"],
}


def suggest_skills(task: str) -> list:
    """
    Suggest relevant skills for a task.
    """
    task_lower = task.lower()
    suggestions = []
    
    for skill, patterns in SKILL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, task_lower):
                if skill not in suggestions:
                    suggestions.append(skill)
    
    return suggestions
