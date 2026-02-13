"""
Skill management system for Oh My Codex.
YAML-based skill files with keyword matching and management.
"""
from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Skill:
    """A skill definition."""
    name: str
    description: str = ""
    keywords: list[str] = field(default_factory=list)
    mode: str = ""
    instructions: str = ""
    model: str = ""
    agents: list[str] = field(default_factory=list)
    author: str = ""
    version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "keywords": self.keywords,
            "mode": self.mode,
            "instructions": self.instructions,
            "model": self.model,
            "agents": self.agents,
            "author": self.author,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Skill:
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            keywords=data.get("keywords", []),
            mode=data.get("mode", ""),
            instructions=data.get("instructions", ""),
            model=data.get("model", ""),
            agents=data.get("agents", []),
            author=data.get("author", ""),
            version=data.get("version", "1.0.0"),
        )


@dataclass
class SkillMatch:
    """Result of matching a prompt to a skill."""
    skill: Skill
    keyword: str
    confidence: float = 1.0


class SkillManager:
    """Manages skill loading, matching, and CRUD operations."""

    def __init__(self, skills_dir: str | Path | None = None) -> None:
        if skills_dir is None:
            self.skills_dir = Path.home() / ".codex" / "skills"
        else:
            self.skills_dir = Path(skills_dir)
        self._cache: dict[str, Skill] = {}

    def _skill_file(self, name: str) -> Path:
        """Get skill file path."""
        skill_dir = self.skills_dir / name
        return skill_dir / "skill.json"

    def _load_skill(self, name: str) -> Skill | None:
        """Load a single skill from disk."""
        skill_file = self._skill_file(name)
        if not skill_file.exists():
            # Try SKILL.md (legacy format)
            md_file = self.skills_dir / name / "SKILL.md"
            if md_file.exists():
                return self._parse_skill_md(name, md_file)
            return None
        try:
            data = json.loads(skill_file.read_text())
            data["name"] = name
            return Skill.from_dict(data)
        except (json.JSONDecodeError, OSError):
            return None

    def _parse_skill_md(self, name: str, path: Path) -> Skill:
        """Parse legacy SKILL.md format."""
        content = path.read_text()
        lines = content.split("\n")
        title = ""
        description = ""
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
            elif title and line.strip() and not description:
                description = line.strip()
                break
        return Skill(name=name, description=description or title)

    def list_skills(self) -> list[Skill]:
        """List all installed skills."""
        if not self.skills_dir.exists():
            return []
        skills = []
        for d in sorted(self.skills_dir.iterdir()):
            if d.is_dir():
                skill = self._load_skill(d.name)
                if skill:
                    skills.append(skill)
        return skills

    def get_skill(self, name: str) -> Skill | None:
        """Get a skill by name."""
        if name in self._cache:
            return self._cache[name]
        skill = self._load_skill(name)
        if skill:
            self._cache[name] = skill
        return skill

    def install_skill(self, skill: Skill) -> bool:
        """Install/save a skill to disk."""
        try:
            skill_dir = self.skills_dir / skill.name
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_file = skill_dir / "skill.json"
            skill_file.write_text(json.dumps(skill.to_dict(), indent=2))
            self._cache[skill.name] = skill
            return True
        except OSError:
            return False

    def uninstall_skill(self, name: str) -> bool:
        """Remove a skill from disk."""
        skill_dir = self.skills_dir / name
        if not skill_dir.exists():
            return False
        try:
            shutil.rmtree(skill_dir)
            self._cache.pop(name, None)
            return True
        except OSError:
            return False

    def search(self, query: str) -> list[Skill]:
        """Search skills by name, description, or keywords."""
        query_lower = query.lower()
        results = []
        for skill in self.list_skills():
            if (query_lower in skill.name.lower()
                or query_lower in skill.description.lower()
                or any(query_lower in kw.lower() for kw in skill.keywords)):
                results.append(skill)
        return results

    def match_prompt(self, prompt: str) -> SkillMatch | None:
        """Match a prompt to a skill via keywords."""
        prompt_lower = prompt.lower()
        best_match: SkillMatch | None = None

        for skill in self.list_skills():
            for keyword in skill.keywords:
                kw_lower = keyword.lower()
                if kw_lower in prompt_lower:
                    # Longer keyword = higher confidence
                    confidence = len(keyword) / max(len(prompt), 1)
                    if best_match is None or confidence > best_match.confidence:
                        best_match = SkillMatch(skill=skill, keyword=keyword, confidence=confidence)

        return best_match

    def create_from_template(self, name: str, description: str = "", keywords: list[str] | None = None, mode: str = "") -> Skill:
        """Create a new skill from template."""
        skill = Skill(
            name=name,
            description=description,
            keywords=keywords or [],
            mode=mode,
            instructions=f"# {name}\n\n{description}\n\n## Instructions\n\nAdd your skill instructions here.",
        )
        self.install_skill(skill)
        return skill

    def export_skill(self, name: str) -> str | None:
        """Export a skill as JSON string."""
        skill = self.get_skill(name)
        if skill is None:
            return None
        return json.dumps(skill.to_dict(), indent=2)

    def import_skill(self, json_str: str) -> Skill | None:
        """Import a skill from JSON string."""
        try:
            data = json.loads(json_str)
            skill = Skill.from_dict(data)
            if skill.name:
                self.install_skill(skill)
                return skill
            return None
        except (json.JSONDecodeError, KeyError):
            return None
