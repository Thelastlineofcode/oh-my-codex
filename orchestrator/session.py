"""
Session management for Oh My Codex.
Handles saving/resuming state for long-running tasks.
"""
from __future__ import annotations

import json
import os
import tempfile
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from dataclasses import dataclass, asdict
from enum import Enum

from .constants import SESSION_ID_UNIQUE_LENGTH, SESSION_CLEANUP_DAYS


class SessionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskRecord:
    """Record of a subtask within a session."""
    id: str
    description: str
    agent: str
    status: str  # pending, in_progress, completed, failed
    result: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None


@dataclass
class Session:
    """Represents an orchestration session."""
    id: str
    task: str
    status: SessionStatus
    created_at: str
    updated_at: str
    mode: str  # autopilot, ultrawork, plan, eco
    tasks: list[TaskRecord]
    context: dict[str, Any]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task": self.task,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "mode": self.mode,
            "tasks": [asdict(t) for t in self.tasks],
            "context": self.context,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Session:
        return cls(
            id=data["id"],
            task=data["task"],
            status=SessionStatus(data["status"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            mode=data["mode"],
            tasks=[TaskRecord(**t) for t in data.get("tasks", [])],
            context=data.get("context", {}),
        )


class SessionManager:
    """Manages session persistence and retrieval."""
    
    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir or os.path.expanduser("~/.codex/sessions"))
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_id(self, task: str) -> str:
        """Generate a unique session ID using UUID4."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:SESSION_ID_UNIQUE_LENGTH]
        return f"{timestamp}_{unique_id}"
    
    def _get_session_path(self, session_id: str) -> Path:
        """Get the file path for a session."""
        return self.base_dir / f"{session_id}.json"
    
    def create(self, task: str, mode: str = "autopilot") -> Session:
        """Create a new session."""
        now = datetime.now().isoformat()
        session = Session(
            id=self._generate_id(task),
            task=task,
            status=SessionStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            mode=mode,
            tasks=[],
            context={},
        )
        self.save(session)
        return session
    
    def save(self, session: Session) -> None:
        """Save a session to disk with atomic write."""
        session.updated_at = datetime.now().isoformat()
        path = self._get_session_path(session.id)
        
        # Atomic write: write to temp file, then move
        fd, tmp_path = tempfile.mkstemp(dir=self.base_dir, suffix='.tmp')
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
            shutil.move(tmp_path, path)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise
    
    def load(self, session_id: str) -> Session | None:
        """Load a session from disk."""
        path = self._get_session_path(session_id)
        if not path.exists():
            return None
        with open(path) as f:
            return Session.from_dict(json.load(f))
    
    def list_sessions(self, status: SessionStatus | None = None) -> list[Session]:
        """List all sessions, optionally filtered by status."""
        sessions = []
        for path in self.base_dir.glob("*.json"):
            try:
                with open(path) as f:
                    session = Session.from_dict(json.load(f))
                    if status is None or session.status == status:
                        sessions.append(session)
            except Exception:
                continue
        return sorted(sessions, key=lambda s: s.created_at, reverse=True)
    
    def get_active(self) -> list[Session]:
        """Get all active sessions."""
        return self.list_sessions(SessionStatus.ACTIVE)
    
    def add_task(self, session: Session, task: TaskRecord) -> None:
        """Add a task to a session."""
        session.tasks.append(task)
        self.save(session)
    
    def update_task(self, session: Session, task_id: str, **updates) -> None:
        """Update a task within a session."""
        for task in session.tasks:
            if task.id == task_id:
                for key, value in updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                break
        self.save(session)
    
    def complete(self, session: Session, success: bool = True) -> None:
        """Mark a session as completed or failed."""
        session.status = SessionStatus.COMPLETED if success else SessionStatus.FAILED
        self.save(session)
    
    def pause(self, session: Session) -> None:
        """Pause a session for later resumption."""
        session.status = SessionStatus.PAUSED
        self.save(session)
    
    def resume(self, session_id: str) -> Session | None:
        """Resume a paused or active session."""
        session = self.load(session_id)
        if session and session.status in [SessionStatus.PAUSED, SessionStatus.ACTIVE]:
            session.status = SessionStatus.ACTIVE
            self.save(session)
            return session
        return None
    
    def cleanup_old(self, days: int = SESSION_CLEANUP_DAYS) -> int:
        """Remove sessions older than specified days."""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        removed = 0
        
        for path in self.base_dir.glob("*.json"):
            try:
                with open(path) as f:
                    data = json.load(f)
                created = datetime.fromisoformat(data["created_at"])
                if created < cutoff:
                    path.unlink()
                    removed += 1
            except Exception:
                continue
        
        return removed
