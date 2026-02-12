"""
Model routing and task classification for Oh My Codex.
"""
from __future__ import annotations

import re
from enum import Enum
from dataclasses import dataclass

from .constants import MODEL_FAST, MODEL_STANDARD, MODEL_POWERFUL


class TaskComplexity(Enum):
    TRIVIAL = (0, "trivial")    # One-liner, typo fix
    SIMPLE = (1, "simple")      # Single file, clear task
    MEDIUM = (2, "medium")      # Multi-file, some complexity
    COMPLEX = (3, "complex")    # Architecture, multi-component
    CRITICAL = (4, "critical")  # Security, production, high-stakes
    
    def __init__(self, order: int, label: str) -> None:
        self.order = order
        self.label = label
    
    def __str__(self) -> str:
        return self.label


class ModelTier(Enum):
    FAST = MODEL_FAST
    STANDARD = MODEL_STANDARD
    POWERFUL = MODEL_POWERFUL


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

def classify_complexity(task: str) -> tuple[TaskComplexity, float]:
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
    
    # Return highest complexity with most matches (using order for proper sorting)
    best = max(matches.items(), key=lambda x: (x[0].order, x[1]))
    confidence = min(0.9, 0.5 + (best[1] * 0.2))
    return best[0], confidence


def detect_mode(task: str) -> tuple[str | None, str]:
    """
    Detect execution mode from task keywords.
    Returns (mode, cleaned_task).
    Uses MODE_KEYWORDS from constants.py for consistency.
    """
    from .constants import MODE_KEYWORDS
    
    task_lower = task.lower()
    
    for keyword, mode in MODE_KEYWORDS.items():
        if task_lower.startswith(keyword):
            return mode, task[len(keyword):].strip()
    
    return None, task


def select_model(complexity: TaskComplexity, mode: str | None = None) -> str:
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
    reasons.append(f"complexity={complexity.label}")
    reasons.append(f"model={model}")
    
    return RoutingDecision(
        model=model,
        complexity=complexity,
        mode=mode,
        confidence=confidence,
        reason=", ".join(reasons),
    )

# Note: suggest_skills() removed in code review cleanup (unused function)
