"""Tests for HUD module."""

import pytest
from unittest.mock import MagicMock, patch

from orchestrator.hud import (
    HUDPreset,
    HUDColors,
    HUDData,
    HUDRenderer,
    HUD,
)


class TestHUDPreset:
    """Tests for HUDPreset enum."""

    def test_preset_values(self):
        assert HUDPreset.MINIMAL.value == "minimal"
        assert HUDPreset.FOCUSED.value == "focused"
        assert HUDPreset.FULL.value == "full"


class TestHUDColors:
    """Tests for HUDColors."""

    def test_mode_color_autopilot(self):
        assert HUDColors.for_mode("autopilot") == "\033[36m"

    def test_mode_color_ralph(self):
        assert HUDColors.for_mode("ralph") == "\033[31m"

    def test_mode_color_unknown(self):
        assert HUDColors.for_mode("unknown_mode") == HUDColors.WHITE


class TestHUDData:
    """Tests for HUDData dataclass."""

    def test_empty_data(self):
        data = HUDData()
        assert data.mode == ""
        assert data.agents == []
        assert data.tokens == {}

    def test_data_with_values(self):
        data = HUDData(
            mode="autopilot",
            phase="executing",
            iteration=2,
            agents=["PM", "BACKEND"],
            total_tokens=5000,
        )
        assert data.mode == "autopilot"
        assert len(data.agents) == 2


class TestHUDRenderer:
    """Tests for HUDRenderer."""

    def test_render_minimal_no_mode(self):
        renderer = HUDRenderer()
        data = HUDData()
        output = renderer.render(data, HUDPreset.MINIMAL)
        assert "No active mode" in output

    def test_render_minimal_with_mode(self):
        renderer = HUDRenderer()
        data = HUDData(mode="autopilot", phase="executing", agents=["PM"], total_tokens=1500)
        output = renderer.render(data, HUDPreset.MINIMAL)
        assert "AUTOPILOT" in output
        assert "1 agents" in output
        assert "1.5K" in output

    def test_render_minimal_with_iteration(self):
        renderer = HUDRenderer()
        data = HUDData(mode="ralph", phase="retrying", iteration=3)
        output = renderer.render(data, HUDPreset.MINIMAL)
        assert "iter 3" in output

    def test_render_focused_no_mode(self):
        renderer = HUDRenderer()
        data = HUDData()
        output = renderer.render(data, HUDPreset.FOCUSED)
        assert "No active mode" in output

    def test_render_focused_with_data(self):
        renderer = HUDRenderer()
        data = HUDData(
            mode="ultrawork",
            phase="parallel",
            agents=["PM", "BACKEND", "FRONTEND"],
            tokens={"PM": 1000, "BACKEND": 2000, "FRONTEND": 1500},
            total_tokens=4500,
            uptime="5m 30s",
        )
        output = renderer.render(data, HUDPreset.FOCUSED)
        assert "ULTRAWORK" in output
        assert "PM" in output
        assert "4.5K" in output

    def test_render_full_no_mode(self):
        renderer = HUDRenderer()
        data = HUDData()
        output = renderer.render(data, HUDPreset.FULL)
        assert "No active mode" in output

    def test_render_full_with_data(self):
        renderer = HUDRenderer()
        data = HUDData(
            mode="autopilot",
            phase="verifying",
            iteration=1,
            agents=["PM", "TESTER"],
            tokens={"PM": 3000, "TESTER": 2000},
            total_tokens=5000,
            git_branch="feature/test",
            session_id="sess-123",
            uptime="10m 5s",
            started_at="2026-02-14T10:00:00",
        )
        output = renderer.render(data, HUDPreset.FULL)
        assert "AUTOPILOT" in output
        assert "sess-123" in output
        assert "feature/test" in output
        assert "5.0K" in output

    def test_format_tokens_small(self):
        renderer = HUDRenderer()
        assert renderer._format_tokens(500) == "500"

    def test_format_tokens_thousands(self):
        renderer = HUDRenderer()
        assert renderer._format_tokens(1500) == "1.5K"

    def test_format_tokens_millions(self):
        renderer = HUDRenderer()
        assert renderer._format_tokens(1_500_000) == "1.5M"

    def test_progress_bar(self):
        renderer = HUDRenderer()
        bar = renderer._progress_bar(50, 10)
        assert "█" in bar
        assert "░" in bar


class TestHUD:
    """Tests for HUD controller."""

    def test_hud_no_state_manager(self):
        hud = HUD()
        output = hud.render_string("minimal")
        assert "No active mode" in output

    def test_hud_with_state_manager(self):
        mock_sm = MagicMock()
        mock_sm.get_snapshot.return_value = MagicMock(
            mode="autopilot",
            phase="executing",
            iteration=1,
            active_agents=["PM"],
            total_tokens=1000,
            session_id="sess-1",
            started_at="2026-02-14T10:00:00",
            uptime_seconds=120.0,
        )
        mock_sm.get_token_breakdown.return_value = {"PM": 1000}

        hud = HUD(state_manager=mock_sm)
        output = hud.render_string("minimal")
        assert "AUTOPILOT" in output

    def test_hud_preset_string(self):
        hud = HUD()
        output = hud.render_string("focused")
        assert isinstance(output, str)

    def test_hud_invalid_preset_fallback(self):
        hud = HUD()
        output = hud.render_string("invalid_preset")
        assert isinstance(output, str)

    def test_format_uptime_seconds(self):
        hud = HUD()
        assert hud._format_uptime(30) == "30s"

    def test_format_uptime_minutes(self):
        hud = HUD()
        assert hud._format_uptime(125) == "2m 5s"

    def test_format_uptime_hours(self):
        hud = HUD()
        assert hud._format_uptime(3725) == "1h 2m"

    @patch("orchestrator.hud.subprocess.run")
    def test_get_git_branch(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="main\n")
        hud = HUD()
        assert hud._get_git_branch() == "main"

    @patch("orchestrator.hud.subprocess.run")
    def test_get_git_branch_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        hud = HUD()
        assert hud._get_git_branch() == ""

    def test_show_prints_output(self, capsys):
        hud = HUD()
        hud.show("minimal")
        captured = capsys.readouterr()
        assert "No active mode" in captured.out
