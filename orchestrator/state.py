"""
State management for Oh My Codex.
SQLite-based tracking of mode lifecycle, agent activity, and token usage.
"""
from __future__ import annotations

import sqlite3
import os
import time
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any


# Default constants (can be overridden via constants.py)
_STATE_DB_FILENAME = "omx-state.db"
_STATE_CLEANUP_DAYS = 30


@dataclass
class ModeState:
    """Active mode tracking."""
    mode: str
    session_id: str
    phase: str = "init"
    iteration: int = 0
    started_at: str = ""
    updated_at: str = ""


@dataclass
class AgentActivity:
    """Agent activity log entry."""
    agent_role: str
    action: str
    duration: float = 0.0
    tokens: int = 0
    timestamp: str = ""
    session_id: str = ""


@dataclass
class TokenUsage:
    """Token usage aggregation."""
    session_id: str
    agent_role: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    timestamp: str = ""


@dataclass
class StateSnapshot:
    """Snapshot for HUD consumption."""
    mode: str = ""
    phase: str = ""
    iteration: int = 0
    active_agents: list[str] = field(default_factory=list)
    total_tokens: int = 0
    session_id: str = ""
    started_at: str = ""
    uptime_seconds: float = 0.0


class StateManager:
    """SQLite-based state manager for orchestration tracking."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None:
            state_dir = Path(".omc") / "state"
            state_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(state_dir / _STATE_DB_FILENAME)
        else:
            self.db_path = str(db_path)
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self._local = threading.local()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Get thread-local connection."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
        return self._local.conn

    def _init_db(self) -> None:
        """Initialize database tables."""
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS mode_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode TEXT NOT NULL,
                session_id TEXT NOT NULL,
                phase TEXT DEFAULT 'init',
                iteration INTEGER DEFAULT 0,
                started_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                ended_at TEXT,
                active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS agent_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                agent_role TEXT NOT NULL,
                action TEXT NOT NULL,
                duration REAL DEFAULT 0.0,
                tokens INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS token_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                agent_role TEXT NOT NULL,
                prompt_tokens INTEGER DEFAULT 0,
                completion_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_mode_state_active ON mode_state(active);
            CREATE INDEX IF NOT EXISTS idx_mode_state_session ON mode_state(session_id);
            CREATE INDEX IF NOT EXISTS idx_agent_activity_session ON agent_activity(session_id);
            CREATE INDEX IF NOT EXISTS idx_token_usage_session ON token_usage(session_id);
        """)
        conn.commit()

    def start_mode(self, mode: str, session_id: str) -> ModeState:
        """Start tracking a new mode."""
        now = datetime.now().isoformat()
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO mode_state (mode, session_id, phase, iteration, started_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (mode, session_id, "init", 0, now, now),
        )
        conn.commit()
        return ModeState(mode=mode, session_id=session_id, phase="init", iteration=0, started_at=now, updated_at=now)

    def update_phase(self, session_id: str, phase: str, iteration: int | None = None) -> None:
        """Update the phase of an active mode."""
        now = datetime.now().isoformat()
        conn = self._get_conn()
        if iteration is not None:
            conn.execute(
                "UPDATE mode_state SET phase = ?, iteration = ?, updated_at = ? WHERE session_id = ? AND active = 1",
                (phase, iteration, now, session_id),
            )
        else:
            conn.execute(
                "UPDATE mode_state SET phase = ?, updated_at = ? WHERE session_id = ? AND active = 1",
                (phase, now, session_id),
            )
        conn.commit()

    def end_mode(self, session_id: str) -> None:
        """End an active mode."""
        now = datetime.now().isoformat()
        conn = self._get_conn()
        conn.execute(
            "UPDATE mode_state SET active = 0, ended_at = ?, updated_at = ? WHERE session_id = ? AND active = 1",
            (now, now, session_id),
        )
        conn.commit()

    def log_agent(self, session_id: str, agent_role: str, action: str, duration: float = 0.0, tokens: int = 0) -> AgentActivity:
        """Log an agent activity."""
        now = datetime.now().isoformat()
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO agent_activity (session_id, agent_role, action, duration, tokens, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, agent_role, action, duration, tokens, now),
        )
        conn.commit()
        return AgentActivity(agent_role=agent_role, action=action, duration=duration, tokens=tokens, timestamp=now, session_id=session_id)

    def log_tokens(self, session_id: str, agent_role: str, prompt_tokens: int = 0, completion_tokens: int = 0) -> TokenUsage:
        """Log token usage."""
        now = datetime.now().isoformat()
        total = prompt_tokens + completion_tokens
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO token_usage (session_id, agent_role, prompt_tokens, completion_tokens, total_tokens, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, agent_role, prompt_tokens, completion_tokens, total, now),
        )
        conn.commit()
        return TokenUsage(session_id=session_id, agent_role=agent_role, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, total_tokens=total, timestamp=now)

    def get_active_mode(self) -> ModeState | None:
        """Get the currently active mode."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT mode, session_id, phase, iteration, started_at, updated_at FROM mode_state WHERE active = 1 ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        return ModeState(mode=row["mode"], session_id=row["session_id"], phase=row["phase"], iteration=row["iteration"], started_at=row["started_at"], updated_at=row["updated_at"])

    def get_session_agents(self, session_id: str) -> list[str]:
        """Get distinct agent roles active in a session."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT DISTINCT agent_role FROM agent_activity WHERE session_id = ? ORDER BY agent_role",
            (session_id,),
        ).fetchall()
        return [row["agent_role"] for row in rows]

    def get_session_tokens(self, session_id: str) -> int:
        """Get total tokens used in a session."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT COALESCE(SUM(total_tokens), 0) as total FROM token_usage WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return row["total"] if row else 0

    def get_agent_activities(self, session_id: str) -> list[AgentActivity]:
        """Get all agent activities for a session."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT agent_role, action, duration, tokens, timestamp, session_id FROM agent_activity WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
        return [AgentActivity(agent_role=r["agent_role"], action=r["action"], duration=r["duration"], tokens=r["tokens"], timestamp=r["timestamp"], session_id=r["session_id"]) for r in rows]

    def get_token_breakdown(self, session_id: str) -> dict[str, int]:
        """Get token usage breakdown by agent role."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT agent_role, SUM(total_tokens) as total FROM token_usage WHERE session_id = ? GROUP BY agent_role",
            (session_id,),
        ).fetchall()
        return {row["agent_role"]: row["total"] for row in rows}

    def get_snapshot(self) -> StateSnapshot:
        """Get current state snapshot for HUD."""
        active = self.get_active_mode()
        if active is None:
            return StateSnapshot()

        agents = self.get_session_agents(active.session_id)
        tokens = self.get_session_tokens(active.session_id)

        uptime = 0.0
        if active.started_at:
            try:
                started = datetime.fromisoformat(active.started_at)
                uptime = (datetime.now() - started).total_seconds()
            except (ValueError, TypeError):
                pass

        return StateSnapshot(
            mode=active.mode,
            phase=active.phase,
            iteration=active.iteration,
            active_agents=agents,
            total_tokens=tokens,
            session_id=active.session_id,
            started_at=active.started_at,
            uptime_seconds=uptime,
        )

    def get_all_sessions(self) -> list[dict[str, Any]]:
        """Get all session summaries from mode_state."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT DISTINCT session_id, mode, started_at, ended_at, active FROM mode_state ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]

    def get_agent_stats(self) -> list[dict[str, Any]]:
        """Get aggregate stats per agent role."""
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT agent_role,
                   COUNT(*) as total_actions,
                   COALESCE(SUM(duration), 0) as total_duration,
                   COALESCE(AVG(duration), 0) as avg_duration,
                   COALESCE(SUM(tokens), 0) as total_tokens
            FROM agent_activity
            GROUP BY agent_role
            ORDER BY total_actions DESC
        """).fetchall()
        return [dict(row) for row in rows]

    def get_token_stats(self) -> list[dict[str, Any]]:
        """Get aggregate token stats per agent role."""
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT agent_role,
                   COUNT(*) as entries,
                   COALESCE(SUM(prompt_tokens), 0) as total_prompt,
                   COALESCE(SUM(completion_tokens), 0) as total_completion,
                   COALESCE(SUM(total_tokens), 0) as total_tokens
            FROM token_usage
            GROUP BY agent_role
            ORDER BY total_tokens DESC
        """).fetchall()
        return [dict(row) for row in rows]

    def cleanup(self, days: int | None = None) -> int:
        """Remove data older than specified days."""
        cleanup_days = days if days is not None else _STATE_CLEANUP_DAYS
        cutoff = (datetime.now() - timedelta(days=cleanup_days)).isoformat()
        conn = self._get_conn()

        cursor = conn.execute("DELETE FROM mode_state WHERE started_at < ? AND active = 0", (cutoff,))
        removed = cursor.rowcount
        conn.execute("DELETE FROM agent_activity WHERE timestamp < ?", (cutoff,))
        conn.execute("DELETE FROM token_usage WHERE timestamp < ?", (cutoff,))
        conn.commit()
        return removed

    def close(self) -> None:
        """Close the database connection."""
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None
