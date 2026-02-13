"""
Context persistence and memory system for Oh My Codex.
Compaction-resilient memory with session and global scopes.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class MemoryScope(Enum):
    SESSION = "session"
    GLOBAL = "global"


class MemoryPriority(Enum):
    NORMAL = "normal"
    HIGH = "high"
    PERMANENT = "permanent"


@dataclass
class MemoryEntry:
    """A single memory entry."""
    key: str
    value: str
    scope: MemoryScope = MemoryScope.SESSION
    priority: MemoryPriority = MemoryPriority.NORMAL
    tags: list[str] = field(default_factory=list)
    created_at: float = 0.0
    expires_at: float = 0.0  # 0 = never

    def is_expired(self) -> bool:
        if self.expires_at == 0 or self.priority == MemoryPriority.PERMANENT:
            return False
        return time.time() > self.expires_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "scope": self.scope.value,
            "priority": self.priority.value,
            "tags": self.tags,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryEntry:
        return cls(
            key=data["key"],
            value=data["value"],
            scope=MemoryScope(data.get("scope", "session")),
            priority=MemoryPriority(data.get("priority", "normal")),
            tags=data.get("tags", []),
            created_at=data.get("created_at", 0.0),
            expires_at=data.get("expires_at", 0.0),
        )


class ContextManager:
    """Manages persistent context and memory."""

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        if storage_dir is None:
            self.storage_dir = Path(".omc") / "context"
        else:
            self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._session_memory: dict[str, MemoryEntry] = {}
        self._load_global()

    def _global_file(self) -> Path:
        return self.storage_dir / "global_memory.json"

    def _session_file(self, session_id: str) -> Path:
        return self.storage_dir / f"session_{session_id}.json"

    def _load_global(self) -> None:
        """Load global memory from disk."""
        self._global_memory: dict[str, MemoryEntry] = {}
        path = self._global_file()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                for entry_data in data.get("entries", []):
                    entry = MemoryEntry.from_dict(entry_data)
                    if not entry.is_expired():
                        self._global_memory[entry.key] = entry
            except (json.JSONDecodeError, OSError):
                pass

    def _save_global(self) -> None:
        """Save global memory to disk."""
        entries = [e.to_dict() for e in self._global_memory.values() if not e.is_expired()]
        self._global_file().write_text(json.dumps({"entries": entries}, indent=2))

    def remember(self, key: str, value: str, scope: MemoryScope = MemoryScope.SESSION, priority: MemoryPriority = MemoryPriority.NORMAL, tags: list[str] | None = None, ttl_seconds: float = 0) -> MemoryEntry:
        """Store a memory entry."""
        now = time.time()
        entry = MemoryEntry(
            key=key,
            value=value,
            scope=scope,
            priority=priority,
            tags=tags or [],
            created_at=now,
            expires_at=now + ttl_seconds if ttl_seconds > 0 else 0,
        )
        if scope == MemoryScope.GLOBAL:
            self._global_memory[key] = entry
            self._save_global()
        else:
            self._session_memory[key] = entry
        return entry

    def recall(self, key: str) -> str | None:
        """Retrieve a memory value by key."""
        # Check session first, then global
        if key in self._session_memory:
            entry = self._session_memory[key]
            if not entry.is_expired():
                return entry.value
            del self._session_memory[key]
        if key in self._global_memory:
            entry = self._global_memory[key]
            if not entry.is_expired():
                return entry.value
            del self._global_memory[key]
            self._save_global()
        return None

    def forget(self, key: str) -> bool:
        """Remove a memory entry."""
        found = False
        if key in self._session_memory:
            del self._session_memory[key]
            found = True
        if key in self._global_memory:
            del self._global_memory[key]
            self._save_global()
            found = True
        return found

    def search(self, query: str = "", tags: list[str] | None = None, scope: MemoryScope | None = None) -> list[MemoryEntry]:
        """Search memory entries."""
        results = []
        all_entries = list(self._session_memory.values()) + list(self._global_memory.values())
        for entry in all_entries:
            if entry.is_expired():
                continue
            if scope and entry.scope != scope:
                continue
            if query and query.lower() not in entry.key.lower() and query.lower() not in entry.value.lower():
                continue
            if tags and not any(t in entry.tags for t in tags):
                continue
            results.append(entry)
        return results

    def get_context_injection(self) -> str:
        """Generate context string for injection into prompts."""
        lines = []
        # Priority: permanent first, then high, then normal
        all_entries = list(self._session_memory.values()) + list(self._global_memory.values())
        active = [e for e in all_entries if not e.is_expired()]
        active.sort(key=lambda e: {"permanent": 0, "high": 1, "normal": 2}[e.priority.value])
        for entry in active:
            prefix = "[P]" if entry.priority == MemoryPriority.PERMANENT else "[H]" if entry.priority == MemoryPriority.HIGH else ""
            lines.append(f"{prefix} {entry.key}: {entry.value}")
        return "\n".join(lines)

    def save_session(self, session_id: str) -> bool:
        """Save session memory to disk."""
        try:
            entries = [e.to_dict() for e in self._session_memory.values()]
            path = self._session_file(session_id)
            path.write_text(json.dumps({"session_id": session_id, "entries": entries}, indent=2))
            return True
        except OSError:
            return False

    def load_session(self, session_id: str) -> int:
        """Load session memory from disk."""
        path = self._session_file(session_id)
        if not path.exists():
            return 0
        try:
            data = json.loads(path.read_text())
            count = 0
            for entry_data in data.get("entries", []):
                entry = MemoryEntry.from_dict(entry_data)
                if not entry.is_expired():
                    self._session_memory[entry.key] = entry
                    count += 1
            return count
        except (json.JSONDecodeError, OSError):
            return 0

    def clear_session(self) -> None:
        """Clear session memory."""
        self._session_memory.clear()

    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        removed = 0
        for key in list(self._session_memory):
            if self._session_memory[key].is_expired():
                del self._session_memory[key]
                removed += 1
        for key in list(self._global_memory):
            if self._global_memory[key].is_expired():
                del self._global_memory[key]
                removed += 1
        if removed:
            self._save_global()
        return removed
