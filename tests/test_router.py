"""Tests for router module."""

import pytest
from orchestrator.router import (
    TaskComplexity,
    ModelTier,
    RoutingDecision,
    classify_complexity,
    detect_mode,
    select_model,
    route_task,
)


class TestTaskComplexity:
    """Tests for TaskComplexity enum."""
    
    def test_complexity_order(self):
        """Verify complexity ordering."""
        assert TaskComplexity.TRIVIAL.order < TaskComplexity.SIMPLE.order
        assert TaskComplexity.SIMPLE.order < TaskComplexity.MEDIUM.order
        assert TaskComplexity.MEDIUM.order < TaskComplexity.COMPLEX.order
        assert TaskComplexity.COMPLEX.order < TaskComplexity.CRITICAL.order
    
    def test_complexity_str(self):
        """Verify string representation."""
        assert str(TaskComplexity.TRIVIAL) == "trivial"
        assert str(TaskComplexity.CRITICAL) == "critical"


class TestClassifyComplexity:
    """Tests for classify_complexity function."""
    
    def test_trivial_tasks(self):
        """Trivial tasks should be classified correctly."""
        complexity, confidence = classify_complexity("fix typo in readme")
        assert complexity == TaskComplexity.TRIVIAL
        assert confidence > 0.5
    
    def test_simple_tasks(self):
        """Simple tasks should be classified correctly."""
        complexity, _ = classify_complexity("add a function to utils")
        assert complexity == TaskComplexity.SIMPLE
    
    def test_medium_tasks(self):
        """Medium tasks should be classified correctly."""
        complexity, _ = classify_complexity("refactor the utils module")
        assert complexity == TaskComplexity.MEDIUM
    
    def test_complex_tasks(self):
        """Complex tasks should be classified correctly."""
        complexity, _ = classify_complexity("architect the entire system")
        assert complexity == TaskComplexity.COMPLEX
    
    def test_critical_tasks(self):
        """Critical tasks should be classified correctly."""
        complexity, _ = classify_complexity("fix security vulnerability")
        assert complexity == TaskComplexity.CRITICAL
    
    def test_unknown_defaults_to_simple(self):
        """Unknown tasks should default to SIMPLE with low confidence."""
        complexity, confidence = classify_complexity("do something random xyz")
        assert complexity == TaskComplexity.SIMPLE
        assert confidence == 0.3


class TestDetectMode:
    """Tests for detect_mode function."""
    
    def test_autopilot_mode(self):
        """Detect autopilot mode."""
        mode, clean = detect_mode("autopilot: build a REST API")
        assert mode == "autopilot"
        assert clean == "build a REST API"
    
    def test_ultrawork_mode(self):
        """Detect ultrawork mode with ulw shorthand."""
        mode, clean = detect_mode("ulw: parallel refactor")
        assert mode == "ultrawork"
        assert clean == "parallel refactor"
    
    def test_eco_mode(self):
        """Detect eco mode."""
        mode, clean = detect_mode("eco: quick fix")
        assert mode == "eco"
        assert clean == "quick fix"
    
    def test_plan_mode(self):
        """Detect plan mode."""
        mode, clean = detect_mode("plan: design architecture")
        assert mode == "plan"
        assert clean == "design architecture"
    
    def test_no_mode(self):
        """No mode detected returns None."""
        mode, clean = detect_mode("just do something")
        assert mode is None
        assert clean == "just do something"
    
    def test_case_insensitive(self):
        """Mode detection should be case insensitive."""
        mode, _ = detect_mode("AUTOPILOT: task")
        assert mode == "autopilot"


class TestSelectModel:
    """Tests for select_model function."""
    
    def test_trivial_uses_nano(self):
        """Trivial tasks use nano model."""
        model = select_model(TaskComplexity.TRIVIAL)
        assert model == ModelTier.NANO.value
    
    def test_complex_uses_powerful(self):
        """Complex tasks use powerful model."""
        model = select_model(TaskComplexity.COMPLEX)
        assert model == ModelTier.POWERFUL.value
    
    def test_eco_mode_overrides(self):
        """Eco mode forces mini model regardless of complexity."""
        model = select_model(TaskComplexity.CRITICAL, mode="eco")
        assert model == ModelTier.MINI.value


class TestRouteTask:
    """Tests for route_task function."""
    
    def test_returns_routing_decision(self):
        """route_task returns RoutingDecision."""
        result = route_task("autopilot: build something")
        assert isinstance(result, RoutingDecision)
        assert result.mode == "autopilot"
        assert result.model is not None
        assert result.confidence > 0
    
    def test_eco_task_routing(self):
        """Eco tasks get fast model."""
        result = route_task("eco: quick fix")
        assert result.mode == "eco"
        assert result.model == ModelTier.FAST.value
    
    def test_complex_task_routing(self):
        """Complex tasks get powerful model."""
        result = route_task("architect the entire notification system")
        assert result.complexity == TaskComplexity.COMPLEX
        assert result.model == ModelTier.POWERFUL.value
