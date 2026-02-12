"""Tests for CLI module."""

import pytest
from orchestrator.cli import detect_mode


class TestDetectMode:
    """Tests for CLI mode detection."""
    
    def test_autopilot_colon(self):
        """Detect autopilot: prefix."""
        mode, clean = detect_mode("autopilot: build API")
        assert mode == "autopilot"
        assert clean == "build API"
    
    def test_ulw_shorthand(self):
        """Detect ulw: shorthand for ultrawork."""
        mode, clean = detect_mode("ulw: parallel tasks")
        assert mode == "ultrawork"
        assert clean == "parallel tasks"
    
    def test_eco_mode(self):
        """Detect eco: prefix."""
        mode, clean = detect_mode("eco: quick fix")
        assert mode == "eco"
        assert clean == "quick fix"
    
    def test_plan_mode(self):
        """Detect plan: prefix."""
        mode, clean = detect_mode("plan: design system")
        assert mode == "plan"
        assert clean == "design system"
    
    def test_ralph_mode(self):
        """Detect ralph: prefix."""
        mode, clean = detect_mode("ralph: persistent task")
        assert mode == "ralph"
        assert clean == "persistent task"
    
    def test_team_mode(self):
        """Detect team: prefix."""
        mode, clean = detect_mode("team: collaborative work")
        assert mode == "team"
        assert clean == "collaborative work"
    
    def test_no_prefix(self):
        """No mode prefix returns None."""
        mode, clean = detect_mode("just do something")
        assert mode is None
        assert clean == "just do something"
    
    def test_space_separator(self):
        """Mode with space separator."""
        mode, clean = detect_mode("autopilot build API")
        assert mode == "autopilot"
        assert clean == "build API"
    
    def test_preserves_case_in_prompt(self):
        """Prompt case is preserved after mode detection."""
        mode, clean = detect_mode("eco: Fix README Typo")
        assert clean == "Fix README Typo"
