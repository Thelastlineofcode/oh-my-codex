"""
Session management for Oh My Codex.
Handles saving/resuming state for long-running tasks.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


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
    result: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


@dataclass
class Session:
    """Represents an orchestration session."""
    id: str
    task: str
    status: SessionStatus
    created_at: str
    updated_at: str
    mode: str  # autopilot, ultrawork, plan, eco
    tasks: List[TaskRecord]
    context: Dict[str, Any]
    
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
    def from_dict(cls, data: dict) -> "Session":
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
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or os.path.expanduser("~/.codex/sessions"))
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_id(self, task: str) -> str:
        """Generate a unique session ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_hash = hashlib.md5(task.encode()).hexdigest()[:8]
        return f"{timestamp}_{task_hash}"
    
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
        """Save a session to disk."""
        session.updated_at = datetime.now().isoformat()
        path = self._get_session_path(session.id)
        with open(path, "w") as f:
            json.dump(session.to_dict(), f, indent=2)
    
    def load(self, session_id: str) -> Optional[Session]:
        """Load a session from disk."""
        path = self._get_session_path(session_id)
        if not path.exists():
            return None
        with open(path) as f:
            return Session.from_dict(json.load(f))
    
    def list_sessions(self, status: SessionStatus = None) -> List[Session]:
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
    
    def get_active(self) -> List[Session]:
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
    
    def resume(self, session_id: str) -> Optional[Session]:
        """Resume a paused or active session."""
        session = self.load(session_id)
        if session and session.status in [SessionStatus.PAUSED, SessionStatus.ACTIVE]:
            session.status = SessionStatus.ACTIVE
            self.save(session)
            return session
        return None
    
    def cleanup_old(self, days: int = 30) -> int:
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
