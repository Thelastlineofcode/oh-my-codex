"""Tests for constants module."""

import pytest
from orchestrator.constants import (
    MODE_KEYWORDS,
    ORCHESTRATED_MODES,
    DIRECT_MODES,
    MODE_MODEL_MAP,
    MODEL_MINI,
    MODEL_STANDARD,
    MODEL_POWERFUL,
    SESSION_ID_UNIQUE_LENGTH,
    SESSION_LIST_LIMIT,
    SESSION_CLEANUP_DAYS,
)


class TestModeKeywords:
    """Tests for MODE_KEYWORDS constant."""
    
    def test_autopilot_keywords(self):
        """Autopilot keywords are defined."""
        assert "autopilot:" in MODE_KEYWORDS
        assert MODE_KEYWORDS["autopilot:"] == "autopilot"
    
    def test_ultrawork_keywords(self):
        """Ultrawork and ulw keywords are defined."""
        assert "ulw:" in MODE_KEYWORDS
        assert "ultrawork:" in MODE_KEYWORDS
        assert MODE_KEYWORDS["ulw:"] == "ultrawork"
    
    def test_all_keywords_have_modes(self):
        """All keywords map to valid modes."""
        all_modes = set(ORCHESTRATED_MODES + DIRECT_MODES)
        for keyword, mode in MODE_KEYWORDS.items():
            assert mode in all_modes, f"{keyword} maps to unknown mode {mode}"


class TestModeLists:
    """Tests for mode lists."""
    
    def test_orchestrated_modes(self):
        """Orchestrated modes are defined."""
        assert "autopilot" in ORCHESTRATED_MODES
        assert "ultrawork" in ORCHESTRATED_MODES
        assert "team" in ORCHESTRATED_MODES
    
    def test_direct_modes(self):
        """Direct modes are defined."""
        assert "eco" in DIRECT_MODES
        assert "plan" in DIRECT_MODES
    
    def test_no_overlap(self):
        """Orchestrated and direct modes don't overlap."""
        overlap = set(ORCHESTRATED_MODES) & set(DIRECT_MODES)
        assert len(overlap) == 0, f"Modes in both lists: {overlap}"


class TestModelMapping:
    """Tests for model mapping."""
    
    def test_all_modes_have_models(self):
        """All modes have model mappings."""
        all_modes = ORCHESTRATED_MODES + DIRECT_MODES
        for mode in all_modes:
            assert mode in MODE_MODEL_MAP, f"Mode {mode} has no model mapping"
    
    def test_eco_uses_mini(self):
        """Eco mode uses mini model."""
        assert MODE_MODEL_MAP["eco"] == MODEL_MINI
    
    def test_autopilot_uses_powerful(self):
        """Autopilot uses powerful model."""
        assert MODE_MODEL_MAP["autopilot"] == MODEL_POWERFUL


class TestSessionConstants:
    """Tests for session-related constants."""
    
    def test_session_id_length(self):
        """Session ID length is reasonable."""
        assert SESSION_ID_UNIQUE_LENGTH > 0
        assert SESSION_ID_UNIQUE_LENGTH <= 32
    
    def test_session_list_limit(self):
        """Session list limit is reasonable."""
        assert SESSION_LIST_LIMIT > 0
        assert SESSION_LIST_LIMIT <= 100
    
    def test_cleanup_days(self):
        """Cleanup days is reasonable."""
        assert SESSION_CLEANUP_DAYS > 0
        assert SESSION_CLEANUP_DAYS <= 365
