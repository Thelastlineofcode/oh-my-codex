"""Tests for session module."""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta

from orchestrator.session import (
    SessionStatus,
    TaskRecord,
    Session,
    SessionManager,
)


@pytest.fixture
def temp_session_dir():
    """Create a temporary directory for sessions."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)


@pytest.fixture
def session_manager(temp_session_dir):
    """Create a SessionManager with temp directory."""
    return SessionManager(base_dir=temp_session_dir)


class TestSessionStatus:
    """Tests for SessionStatus enum."""
    
    def test_status_values(self):
        """Verify status values."""
        assert SessionStatus.ACTIVE.value == "active"
        assert SessionStatus.PAUSED.value == "paused"
        assert SessionStatus.COMPLETED.value == "completed"
        assert SessionStatus.FAILED.value == "failed"


class TestTaskRecord:
    """Tests for TaskRecord dataclass."""
    
    def test_create_task_record(self):
        """Create a task record."""
        task = TaskRecord(
            id="task-1",
            description="Test task",
            agent="PM",
            status="pending",
        )
        assert task.id == "task-1"
        assert task.status == "pending"
        assert task.result is None


class TestSession:
    """Tests for Session dataclass."""
    
    def test_to_dict(self):
        """Session converts to dict."""
        session = Session(
            id="test-123",
            task="Test task",
            status=SessionStatus.ACTIVE,
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
            mode="autopilot",
            tasks=[],
            context={},
        )
        data = session.to_dict()
        assert data["id"] == "test-123"
        assert data["status"] == "active"
        assert data["mode"] == "autopilot"
    
    def test_from_dict(self):
        """Session creates from dict."""
        data = {
            "id": "test-456",
            "task": "Another task",
            "status": "completed",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
            "mode": "eco",
            "tasks": [],
            "context": {"key": "value"},
        }
        session = Session.from_dict(data)
        assert session.id == "test-456"
        assert session.status == SessionStatus.COMPLETED
        assert session.context["key"] == "value"


class TestSessionManager:
    """Tests for SessionManager."""
    
    def test_create_session(self, session_manager):
        """Create a new session."""
        session = session_manager.create("Test task", mode="autopilot")
        assert session.task == "Test task"
        assert session.mode == "autopilot"
        assert session.status == SessionStatus.ACTIVE
        assert len(session.id) > 0
    
    def test_save_and_load(self, session_manager):
        """Save and load a session."""
        session = session_manager.create("Persist test")
        session_id = session.id
        
        # Load it back
        loaded = session_manager.load(session_id)
        assert loaded is not None
        assert loaded.id == session_id
        assert loaded.task == "Persist test"
    
    def test_load_nonexistent(self, session_manager):
        """Load nonexistent session returns None."""
        result = session_manager.load("nonexistent-id")
        assert result is None
    
    def test_list_sessions(self, session_manager):
        """List all sessions."""
        session_manager.create("Task 1")
        session_manager.create("Task 2")
        session_manager.create("Task 3")
        
        sessions = session_manager.list_sessions()
        assert len(sessions) == 3
    
    def test_list_sessions_by_status(self, session_manager):
        """List sessions filtered by status."""
        s1 = session_manager.create("Active task")
        s2 = session_manager.create("Completed task")
        session_manager.complete(s2, success=True)
        
        active = session_manager.list_sessions(SessionStatus.ACTIVE)
        completed = session_manager.list_sessions(SessionStatus.COMPLETED)
        
        assert len(active) == 1
        assert len(completed) == 1
        assert active[0].id == s1.id
    
    def test_add_task(self, session_manager):
        """Add a task to session."""
        session = session_manager.create("Parent task")
        task = TaskRecord(
            id="subtask-1",
            description="Subtask",
            agent="BACKEND",
            status="pending",
        )
        session_manager.add_task(session, task)
        
        # Reload and verify
        loaded = session_manager.load(session.id)
        assert len(loaded.tasks) == 1
        assert loaded.tasks[0].id == "subtask-1"
    
    def test_update_task(self, session_manager):
        """Update a task in session."""
        session = session_manager.create("Parent task")
        task = TaskRecord(
            id="subtask-1",
            description="Subtask",
            agent="BACKEND",
            status="pending",
        )
        session_manager.add_task(session, task)
        
        # Update the task
        session_manager.update_task(session, "subtask-1", status="completed", result="Done!")
        
        # Reload and verify
        loaded = session_manager.load(session.id)
        assert loaded.tasks[0].status == "completed"
        assert loaded.tasks[0].result == "Done!"
    
    def test_complete_session(self, session_manager):
        """Complete a session."""
        session = session_manager.create("Task to complete")
        session_manager.complete(session, success=True)
        
        loaded = session_manager.load(session.id)
        assert loaded.status == SessionStatus.COMPLETED
    
    def test_fail_session(self, session_manager):
        """Fail a session."""
        session = session_manager.create("Task to fail")
        session_manager.complete(session, success=False)
        
        loaded = session_manager.load(session.id)
        assert loaded.status == SessionStatus.FAILED
    
    def test_pause_and_resume(self, session_manager):
        """Pause and resume a session."""
        session = session_manager.create("Pausable task")
        session_manager.pause(session)
        
        loaded = session_manager.load(session.id)
        assert loaded.status == SessionStatus.PAUSED
        
        resumed = session_manager.resume(session.id)
        assert resumed.status == SessionStatus.ACTIVE
    
    def test_resume_nonexistent(self, session_manager):
        """Resume nonexistent session returns None."""
        result = session_manager.resume("nonexistent")
        assert result is None
    
    def test_atomic_write(self, session_manager, temp_session_dir):
        """Verify atomic write doesn't leave temp files on success."""
        session = session_manager.create("Atomic test")
        
        # Check no .tmp files remain
        tmp_files = list(Path(temp_session_dir).glob("*.tmp"))
        assert len(tmp_files) == 0
        
        # Session file exists
        session_files = list(Path(temp_session_dir).glob("*.json"))
        assert len(session_files) == 1
    
    def test_unique_session_ids(self, session_manager):
        """Session IDs should be unique."""
        ids = set()
        for _ in range(100):
            session = session_manager.create("Same task")
            ids.add(session.id)
        
        assert len(ids) == 100  # All unique
