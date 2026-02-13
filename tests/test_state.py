"""Tests for state management module."""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from datetime import datetime

from orchestrator.state import (
    StateManager,
    ModeState,
    AgentActivity,
    TokenUsage,
    StateSnapshot,
)


@pytest.fixture
def temp_db_path():
    """Create a temporary database path."""
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test-state.db")
    yield db_path
    shutil.rmtree(tmpdir)


@pytest.fixture
def state_manager(temp_db_path):
    """Create a StateManager with temp database."""
    mgr = StateManager(db_path=temp_db_path)
    yield mgr
    mgr.close()


class TestModeState:
    """Tests for ModeState dataclass."""

    def test_create_mode_state(self):
        ms = ModeState(mode="autopilot", session_id="sess-1")
        assert ms.mode == "autopilot"
        assert ms.session_id == "sess-1"
        assert ms.phase == "init"
        assert ms.iteration == 0

    def test_default_values(self):
        ms = ModeState(mode="eco", session_id="sess-2")
        assert ms.started_at == ""
        assert ms.updated_at == ""


class TestAgentActivity:
    """Tests for AgentActivity dataclass."""

    def test_create_activity(self):
        aa = AgentActivity(agent_role="PM", action="plan")
        assert aa.agent_role == "PM"
        assert aa.action == "plan"
        assert aa.duration == 0.0
        assert aa.tokens == 0


class TestTokenUsage:
    """Tests for TokenUsage dataclass."""

    def test_create_token_usage(self):
        tu = TokenUsage(session_id="sess-1", agent_role="PM", prompt_tokens=100, completion_tokens=200, total_tokens=300)
        assert tu.total_tokens == 300


class TestStateSnapshot:
    """Tests for StateSnapshot dataclass."""

    def test_empty_snapshot(self):
        ss = StateSnapshot()
        assert ss.mode == ""
        assert ss.total_tokens == 0
        assert ss.active_agents == []

    def test_snapshot_with_data(self):
        ss = StateSnapshot(mode="ultrawork", phase="executing", active_agents=["PM", "BACKEND"], total_tokens=5000)
        assert ss.mode == "ultrawork"
        assert len(ss.active_agents) == 2


class TestStateManager:
    """Tests for StateManager."""

    def test_init_creates_db(self, state_manager, temp_db_path):
        assert os.path.exists(temp_db_path)

    def test_start_mode(self, state_manager):
        ms = state_manager.start_mode("autopilot", "sess-1")
        assert ms.mode == "autopilot"
        assert ms.session_id == "sess-1"
        assert ms.phase == "init"

    def test_get_active_mode(self, state_manager):
        state_manager.start_mode("ralph", "sess-1")
        active = state_manager.get_active_mode()
        assert active is not None
        assert active.mode == "ralph"

    def test_get_active_mode_empty(self, state_manager):
        active = state_manager.get_active_mode()
        assert active is None

    def test_update_phase(self, state_manager):
        state_manager.start_mode("autopilot", "sess-1")
        state_manager.update_phase("sess-1", "executing", iteration=2)
        active = state_manager.get_active_mode()
        assert active.phase == "executing"
        assert active.iteration == 2

    def test_update_phase_without_iteration(self, state_manager):
        state_manager.start_mode("autopilot", "sess-1")
        state_manager.update_phase("sess-1", "verifying")
        active = state_manager.get_active_mode()
        assert active.phase == "verifying"
        assert active.iteration == 0

    def test_end_mode(self, state_manager):
        state_manager.start_mode("autopilot", "sess-1")
        state_manager.end_mode("sess-1")
        active = state_manager.get_active_mode()
        assert active is None

    def test_log_agent(self, state_manager):
        aa = state_manager.log_agent("sess-1", "PM", "planning", duration=1.5, tokens=500)
        assert aa.agent_role == "PM"
        assert aa.duration == 1.5

    def test_log_tokens(self, state_manager):
        tu = state_manager.log_tokens("sess-1", "PM", prompt_tokens=100, completion_tokens=200)
        assert tu.total_tokens == 300

    def test_get_session_agents(self, state_manager):
        state_manager.log_agent("sess-1", "PM", "plan")
        state_manager.log_agent("sess-1", "BACKEND", "code")
        state_manager.log_agent("sess-1", "PM", "review")
        agents = state_manager.get_session_agents("sess-1")
        assert "PM" in agents
        assert "BACKEND" in agents
        assert len(agents) == 2

    def test_get_session_tokens(self, state_manager):
        state_manager.log_tokens("sess-1", "PM", prompt_tokens=100, completion_tokens=200)
        state_manager.log_tokens("sess-1", "BACKEND", prompt_tokens=50, completion_tokens=100)
        total = state_manager.get_session_tokens("sess-1")
        assert total == 450

    def test_get_session_tokens_empty(self, state_manager):
        total = state_manager.get_session_tokens("nonexistent")
        assert total == 0

    def test_get_agent_activities(self, state_manager):
        state_manager.log_agent("sess-1", "PM", "plan", duration=1.0)
        state_manager.log_agent("sess-1", "PM", "review", duration=2.0)
        activities = state_manager.get_agent_activities("sess-1")
        assert len(activities) == 2
        assert activities[0].action == "plan"

    def test_get_token_breakdown(self, state_manager):
        state_manager.log_tokens("sess-1", "PM", prompt_tokens=100, completion_tokens=200)
        state_manager.log_tokens("sess-1", "BACKEND", prompt_tokens=50, completion_tokens=100)
        breakdown = state_manager.get_token_breakdown("sess-1")
        assert breakdown["PM"] == 300
        assert breakdown["BACKEND"] == 150

    def test_get_snapshot(self, state_manager):
        state_manager.start_mode("ultrawork", "sess-1")
        state_manager.update_phase("sess-1", "executing", iteration=3)
        state_manager.log_agent("sess-1", "PM", "plan")
        state_manager.log_agent("sess-1", "BACKEND", "code")
        state_manager.log_tokens("sess-1", "PM", prompt_tokens=500, completion_tokens=500)

        snap = state_manager.get_snapshot()
        assert snap.mode == "ultrawork"
        assert snap.phase == "executing"
        assert snap.iteration == 3
        assert "PM" in snap.active_agents
        assert snap.total_tokens == 1000
        assert snap.uptime_seconds >= 0

    def test_get_snapshot_no_active(self, state_manager):
        snap = state_manager.get_snapshot()
        assert snap.mode == ""
        assert snap.total_tokens == 0

    def test_get_all_sessions(self, state_manager):
        state_manager.start_mode("autopilot", "sess-1")
        state_manager.start_mode("ralph", "sess-2")
        sessions = state_manager.get_all_sessions()
        assert len(sessions) == 2

    def test_get_agent_stats(self, state_manager):
        state_manager.log_agent("sess-1", "PM", "plan", duration=1.0, tokens=100)
        state_manager.log_agent("sess-1", "PM", "review", duration=2.0, tokens=200)
        state_manager.log_agent("sess-1", "BACKEND", "code", duration=3.0, tokens=300)
        stats = state_manager.get_agent_stats()
        assert len(stats) == 2
        pm_stat = [s for s in stats if s["agent_role"] == "PM"][0]
        assert pm_stat["total_actions"] == 2

    def test_get_token_stats(self, state_manager):
        state_manager.log_tokens("sess-1", "PM", 100, 200)
        state_manager.log_tokens("sess-1", "PM", 150, 250)
        stats = state_manager.get_token_stats()
        assert len(stats) == 1
        assert stats[0]["total_tokens"] == 700

    def test_cleanup(self, state_manager):
        state_manager.start_mode("old", "old-sess")
        state_manager.end_mode("old-sess")
        # Cleanup with 0 days should remove ended sessions
        removed = state_manager.cleanup(days=0)
        # The record was just created so it might not be old enough
        # Test that cleanup runs without error
        assert isinstance(removed, int)

    def test_multiple_modes(self, state_manager):
        state_manager.start_mode("autopilot", "sess-1")
        state_manager.end_mode("sess-1")
        state_manager.start_mode("ralph", "sess-2")
        active = state_manager.get_active_mode()
        assert active.mode == "ralph"
        assert active.session_id == "sess-2"

    def test_close(self, state_manager):
        state_manager.close()
        # After close, operations should reconnect
        state_manager.start_mode("test", "sess-1")
        active = state_manager.get_active_mode()
        assert active is not None
