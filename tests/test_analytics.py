"""Tests for analytics engine module."""

import pytest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import MagicMock

from orchestrator.analytics import (
    AgentPerformanceMetrics,
    ModelEfficiency,
    Recommendation,
    AnalyticsSummary,
    AnalyticsEngine,
)


def make_mock_state_manager(agent_stats=None, token_stats=None, sessions=None, session_tokens=None):
    """Create a mock StateManager with configurable data."""
    mock = MagicMock()
    mock.get_agent_stats.return_value = agent_stats or []
    mock.get_token_stats.return_value = token_stats or []
    mock.get_all_sessions.return_value = sessions or []

    # Configure get_session_tokens to return tokens per session
    if session_tokens:
        mock.get_session_tokens.side_effect = lambda sid: session_tokens.get(sid, 0)
    else:
        mock.get_session_tokens.return_value = 0

    return mock


class TestAgentPerformanceMetrics:
    """Tests for AgentPerformanceMetrics dataclass."""

    def test_create_metrics(self):
        m = AgentPerformanceMetrics(agent_role="PM", total_actions=10, avg_duration=1.5)
        assert m.agent_role == "PM"
        assert m.total_actions == 10
        assert m.token_efficiency == 0.0


class TestModelEfficiency:
    """Tests for ModelEfficiency dataclass."""

    def test_create_efficiency(self):
        m = ModelEfficiency(model="autopilot", total_sessions=5, total_tokens=10000)
        assert m.model == "autopilot"
        assert m.avg_tokens_per_session == 0.0


class TestRecommendation:
    """Tests for Recommendation dataclass."""

    def test_create_recommendation(self):
        r = Recommendation(category="mode", suggestion="Use eco", reason="Save tokens", confidence=0.8)
        assert r.confidence == 0.8


class TestAnalyticsEngine:
    """Tests for AnalyticsEngine."""

    def test_no_state_manager(self):
        engine = AnalyticsEngine()
        metrics = engine.get_agent_metrics()
        assert metrics == []

    def test_no_state_manager_recommendations(self):
        engine = AnalyticsEngine()
        recs = engine.get_recommendations()
        assert len(recs) == 1
        assert recs[0].category == "setup"

    def test_empty_data_recommendations(self):
        mock_sm = make_mock_state_manager()
        engine = AnalyticsEngine(state_manager=mock_sm)
        recs = engine.get_recommendations()
        assert len(recs) == 1
        assert recs[0].category == "data"

    def test_get_agent_metrics(self):
        mock_sm = make_mock_state_manager(
            agent_stats=[
                {"agent_role": "PM", "total_actions": 10, "total_duration": 15.0, "avg_duration": 1.5, "total_tokens": 5000},
                {"agent_role": "BACKEND", "total_actions": 5, "total_duration": 20.0, "avg_duration": 4.0, "total_tokens": 3000},
            ],
            token_stats=[
                {"agent_role": "PM", "total_tokens": 5000},
                {"agent_role": "BACKEND", "total_tokens": 3000},
            ],
        )
        engine = AnalyticsEngine(state_manager=mock_sm)
        metrics = engine.get_agent_metrics()
        assert len(metrics) == 2
        assert metrics[0].agent_role == "PM"
        assert metrics[0].total_actions == 10
        assert metrics[0].token_efficiency > 0

    def test_get_model_efficiency(self):
        mock_sm = make_mock_state_manager(
            sessions=[
                {"session_id": "s1", "mode": "autopilot", "started_at": "", "ended_at": "", "active": 0},
                {"session_id": "s2", "mode": "autopilot", "started_at": "", "ended_at": "", "active": 0},
                {"session_id": "s3", "mode": "ralph", "started_at": "", "ended_at": "", "active": 0},
            ],
            session_tokens={"s1": 1000, "s2": 2000, "s3": 3000},
        )
        engine = AnalyticsEngine(state_manager=mock_sm)
        metrics = engine.get_model_efficiency()
        assert len(metrics) == 2
        autopilot = [m for m in metrics if m.model == "autopilot"][0]
        assert autopilot.total_sessions == 2
        assert autopilot.total_tokens == 3000

    def test_get_summary(self):
        mock_sm = make_mock_state_manager(
            agent_stats=[
                {"agent_role": "PM", "total_actions": 10, "total_duration": 15.0, "avg_duration": 1.5, "total_tokens": 5000},
            ],
            token_stats=[
                {"agent_role": "PM", "total_tokens": 5000},
            ],
            sessions=[
                {"session_id": "s1", "mode": "autopilot", "started_at": "", "ended_at": "", "active": 0},
            ],
            session_tokens={"s1": 5000},
        )
        engine = AnalyticsEngine(state_manager=mock_sm)
        summary = engine.get_summary()
        assert summary.total_sessions == 1
        assert summary.total_tokens == 5000
        assert len(summary.agent_metrics) == 1
        assert summary.most_used_mode == "autopilot"

    def test_export_json(self):
        mock_sm = make_mock_state_manager(
            agent_stats=[
                {"agent_role": "PM", "total_actions": 5, "total_duration": 10.0, "avg_duration": 2.0, "total_tokens": 1000},
            ],
            token_stats=[{"agent_role": "PM", "total_tokens": 1000}],
            sessions=[
                {"session_id": "s1", "mode": "autopilot", "started_at": "", "ended_at": "", "active": 0},
            ],
            session_tokens={"s1": 1000},
        )
        engine = AnalyticsEngine(state_manager=mock_sm)
        result = engine.export_json()
        data = json.loads(result)
        assert "total_sessions" in data
        assert "agent_metrics" in data

    def test_export_csv(self):
        mock_sm = make_mock_state_manager(
            agent_stats=[
                {"agent_role": "PM", "total_actions": 5, "total_duration": 10.0, "avg_duration": 2.0, "total_tokens": 1000},
            ],
            token_stats=[{"agent_role": "PM", "total_tokens": 1000}],
        )
        engine = AnalyticsEngine(state_manager=mock_sm)
        result = engine.export_csv()
        assert "agent_role" in result
        assert "PM" in result

    def test_export_csv_empty(self):
        engine = AnalyticsEngine()
        result = engine.export_csv()
        assert "agent_role" in result  # Header still present

    def test_format_summary(self):
        mock_sm = make_mock_state_manager(
            agent_stats=[
                {"agent_role": "PM", "total_actions": 10, "total_duration": 15.0, "avg_duration": 1.5, "total_tokens": 5000},
            ],
            token_stats=[{"agent_role": "PM", "total_tokens": 5000}],
            sessions=[
                {"session_id": "s1", "mode": "autopilot", "started_at": "", "ended_at": "", "active": 0},
            ],
            session_tokens={"s1": 5000},
        )
        engine = AnalyticsEngine(state_manager=mock_sm)
        output = engine.format_summary()
        assert "OMX Analytics" in output
        assert "Sessions" in output

    def test_format_tokens(self):
        engine = AnalyticsEngine()
        assert engine._format_tokens(500) == "500"
        assert engine._format_tokens(1500) == "1.5K"
        assert engine._format_tokens(1_500_000) == "1.5M"

    def test_recommendation_inefficient_agent(self):
        mock_sm = make_mock_state_manager(
            agent_stats=[
                {"agent_role": "PM", "total_actions": 2, "total_duration": 60.0, "avg_duration": 30.0, "total_tokens": 50000},
            ],
            token_stats=[{"agent_role": "PM", "total_tokens": 50000}],
            sessions=[
                {"session_id": "s1", "mode": "autopilot", "started_at": "", "ended_at": "", "active": 0},
            ],
            session_tokens={"s1": 50000},
        )
        engine = AnalyticsEngine(state_manager=mock_sm)
        recs = engine.get_recommendations()
        agent_recs = [r for r in recs if r.category == "agent"]
        assert len(agent_recs) >= 1

    def test_recommendation_only_autopilot(self):
        mock_sm = make_mock_state_manager(
            agent_stats=[
                {"agent_role": "PM", "total_actions": 10, "total_duration": 10.0, "avg_duration": 1.0, "total_tokens": 1000},
            ],
            token_stats=[{"agent_role": "PM", "total_tokens": 1000}],
            sessions=[
                {"session_id": "s1", "mode": "autopilot", "started_at": "", "ended_at": "", "active": 0},
            ],
            session_tokens={"s1": 1000},
        )
        engine = AnalyticsEngine(state_manager=mock_sm)
        recs = engine.get_recommendations()
        mode_recs = [r for r in recs if r.category == "mode"]
        suggestions = [r.suggestion for r in mode_recs]
        assert any("ultrawork" in s.lower() for s in suggestions)
