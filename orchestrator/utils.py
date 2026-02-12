"""
Utility functions for Oh My Codex.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List


def get_codex_dir() -> Path:
    """Get the Codex configuration directory."""
    return Path.home() / ".codex"


def get_skills_dir() -> Path:
    """Get the skills directory."""
    return get_codex_dir() / "skills"


def get_sessions_dir() -> Path:
    """Get the sessions directory."""
    return get_codex_dir() / "sessions"


def get_plans_dir() -> Path:
    """Get the plans directory."""
    return get_codex_dir() / "plans"


def ensure_dirs():
    """Ensure all required directories exist."""
    dirs = [
        get_codex_dir(),
        get_skills_dir(),
        get_sessions_dir(),
        get_plans_dir(),
        get_codex_dir() / "errors",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def list_installed_skills() -> List[str]:
    """List installed skill names."""
    skills_dir = get_skills_dir()
    if not skills_dir.exists():
        return []
    return [
        d.name for d in skills_dir.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    ]


def get_skill_info(skill_name: str) -> Optional[Dict[str, Any]]:
    """Get information about a skill."""
    skill_dir = get_skills_dir() / skill_name
    skill_file = skill_dir / "SKILL.md"
    
    if not skill_file.exists():
        return None
    
    content = skill_file.read_text()
    
    # Parse basic info from markdown
    lines = content.split("\n")
    title = ""
    description = ""
    
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
        elif not title and line.strip():
            continue
        elif title and line.strip() and not description:
            description = line.strip()
            break
    
    return {
        "name": skill_name,
        "title": title,
        "description": description,
        "path": str(skill_dir),
    }


def generate_task_id(task: str) -> str:
    """Generate a unique task ID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_hash = hashlib.md5(task.encode()).hexdigest()[:8]
    return f"{timestamp}_{task_hash}"


def save_plan(task: str, plan: str, name: Optional[str] = None) -> Path:
    """Save a plan document."""
    plans_dir = get_plans_dir()
    plans_dir.mkdir(parents=True, exist_ok=True)
    
    if name:
        filename = f"{name}.md"
    else:
        filename = f"{generate_task_id(task)}.md"
    
    plan_path = plans_dir / filename
    
    content = f"""# Plan: {task[:50]}

Generated: {datetime.now().isoformat()}

---

{plan}
"""
    
    plan_path.write_text(content)
    return plan_path


def load_plan(plan_id: str) -> Optional[str]:
    """Load a plan document."""
    plans_dir = get_plans_dir()
    
    # Try with and without .md extension
    for ext in ["", ".md"]:
        plan_path = plans_dir / f"{plan_id}{ext}"
        if plan_path.exists():
            return plan_path.read_text()
    
    return None


def list_plans() -> List[Dict[str, Any]]:
    """List all saved plans."""
    plans_dir = get_plans_dir()
    if not plans_dir.exists():
        return []
    
    plans = []
    for f in plans_dir.glob("*.md"):
        content = f.read_text()
        lines = content.split("\n")
        title = ""
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break
        
        plans.append({
            "id": f.stem,
            "title": title,
            "path": str(f),
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })
    
    return sorted(plans, key=lambda x: x["modified"], reverse=True)


def log_error(error: str, context: Dict[str, Any] = None):
    """Log an error for debugging."""
    errors_dir = get_codex_dir() / "errors"
    errors_dir.mkdir(parents=True, exist_ok=True)
    
    error_file = errors_dir / f"{generate_task_id('error')}.json"
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "error": error,
        "context": context or {},
    }
    
    error_file.write_text(json.dumps(data, indent=2))
    return error_file


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_duration(seconds: float) -> str:
    """Format duration in human-readable form."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def parse_agents_md(path: Path = None) -> Dict[str, Any]:
    """Parse AGENTS.md for configuration."""
    if path is None:
        # Look in current directory first, then home
        candidates = [
            Path.cwd() / "AGENTS.md",
            get_codex_dir() / "AGENTS.md",
        ]
        for p in candidates:
            if p.exists():
                path = p
                break
    
    if not path or not path.exists():
        return {}
    
    content = path.read_text()
    
    # Extract key sections (basic parsing)
    result = {
        "path": str(path),
        "content": content,
    }
    
    # Find keyword detection table
    if "Keyword Detection" in content:
        result["has_keywords"] = True
    
    # Find skill routing table
    if "Skill Routing" in content:
        result["has_routing"] = True
    
    return result
