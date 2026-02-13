"""Tests for verification protocol module."""

import pytest
import subprocess
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from orchestrator.verify import (
    VerificationTier,
    Evidence,
    VerificationResult,
    ProjectConfig,
    ProjectDetector,
    Verifier,
)


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)


class TestVerificationTier:
    """Tests for VerificationTier enum."""

    def test_tier_values(self):
        assert VerificationTier.LIGHT.value == "light"
        assert VerificationTier.STANDARD.value == "standard"
        assert VerificationTier.THOROUGH.value == "thorough"


class TestEvidence:
    """Tests for Evidence dataclass."""

    def test_create_evidence(self):
        e = Evidence(check_type="test", command="pytest", status="pass")
        assert e.check_type == "test"
        assert e.status == "pass"
        assert e.duration == 0.0

    def test_evidence_with_output(self):
        e = Evidence(check_type="lint", command="ruff check .", status="fail", output="Error line 1")
        assert "Error" in e.output


class TestVerificationResult:
    """Tests for VerificationResult dataclass."""

    def test_passed_result(self):
        r = VerificationResult(tier=VerificationTier.LIGHT, passed=True, confidence=1.0)
        assert r.passed is True
        assert r.retry_count == 0

    def test_failed_result(self):
        r = VerificationResult(
            tier=VerificationTier.STANDARD,
            passed=False,
            evidence=[Evidence(check_type="test", command="pytest", status="fail")],
            confidence=0.0,
        )
        assert r.passed is False
        assert len(r.evidence) == 1


class TestProjectConfig:
    """Tests for ProjectConfig dataclass."""

    def test_default_config(self):
        pc = ProjectConfig(project_type="unknown")
        assert pc.project_type == "unknown"
        assert pc.test_cmd == []
        assert pc.build_cmd == []


class TestProjectDetector:
    """Tests for ProjectDetector."""

    def test_detect_python_pyproject(self, temp_project_dir):
        (temp_project_dir / "pyproject.toml").write_text('[tool.pytest.ini_options]\n')
        (temp_project_dir / "tests").mkdir()
        detector = ProjectDetector(temp_project_dir)
        config = detector.detect()
        assert config.project_type == "python"
        assert "pytest" in config.test_cmd

    def test_detect_python_setup_py(self, temp_project_dir):
        (temp_project_dir / "setup.py").write_text("from setuptools import setup\nsetup()")
        detector = ProjectDetector(temp_project_dir)
        config = detector.detect()
        assert config.project_type == "python"

    def test_detect_node(self, temp_project_dir):
        pkg = {"name": "test", "scripts": {"test": "jest", "build": "tsc", "lint": "eslint ."}}
        (temp_project_dir / "package.json").write_text(json.dumps(pkg))
        detector = ProjectDetector(temp_project_dir)
        config = detector.detect()
        assert config.project_type == "node"
        assert config.test_cmd == ["npm", "test"]
        assert config.build_cmd == ["npm", "run", "build"]

    def test_detect_node_with_tsconfig(self, temp_project_dir):
        pkg = {"name": "test", "scripts": {"test": "jest"}}
        (temp_project_dir / "package.json").write_text(json.dumps(pkg))
        (temp_project_dir / "tsconfig.json").write_text("{}")
        detector = ProjectDetector(temp_project_dir)
        config = detector.detect()
        assert config.typecheck_cmd == ["npx", "tsc", "--noEmit"]

    def test_detect_rust(self, temp_project_dir):
        (temp_project_dir / "Cargo.toml").write_text('[package]\nname = "test"')
        detector = ProjectDetector(temp_project_dir)
        config = detector.detect()
        assert config.project_type == "rust"
        assert config.test_cmd == ["cargo", "test"]
        assert config.build_cmd == ["cargo", "build"]

    def test_detect_go(self, temp_project_dir):
        (temp_project_dir / "go.mod").write_text("module test")
        detector = ProjectDetector(temp_project_dir)
        config = detector.detect()
        assert config.project_type == "go"
        assert config.test_cmd == ["go", "test", "./..."]

    def test_detect_unknown(self, temp_project_dir):
        detector = ProjectDetector(temp_project_dir)
        config = detector.detect()
        assert config.project_type == "unknown"


class TestVerifier:
    """Tests for Verifier."""

    def test_classify_light(self):
        v = Verifier()
        assert v.classify_tier(2, 50) == VerificationTier.LIGHT

    def test_classify_standard(self):
        v = Verifier()
        assert v.classify_tier(10, 300) == VerificationTier.STANDARD

    def test_classify_thorough(self):
        v = Verifier()
        assert v.classify_tier(20, 600) == VerificationTier.THOROUGH

    def test_classify_boundary_light(self):
        v = Verifier()
        assert v.classify_tier(3, 99) == VerificationTier.LIGHT

    def test_classify_boundary_standard(self):
        v = Verifier()
        assert v.classify_tier(4, 100) == VerificationTier.STANDARD

    def test_verify_skip_mode(self):
        v = Verifier()
        result = v.verify(mode="plan")
        assert result.passed is True
        assert result.evidence[0].status == "skip"

    def test_verify_skip_eco(self):
        v = Verifier()
        result = v.verify(mode="eco")
        assert result.passed is True

    def test_verify_skip_research(self):
        v = Verifier()
        result = v.verify(mode="research")
        assert result.passed is True

    @patch("orchestrator.verify.subprocess.run")
    def test_verify_light_pass(self, mock_run, temp_project_dir):
        (temp_project_dir / "pyproject.toml").write_text('[tool.pytest]\n')
        (temp_project_dir / "tests").mkdir()
        mock_run.return_value = MagicMock(returncode=0, stdout="All tests passed", stderr="")

        v = Verifier(root=temp_project_dir)
        result = v.verify(tier=VerificationTier.LIGHT)
        assert result.passed is True
        assert result.confidence == 1.0

    @patch("orchestrator.verify.subprocess.run")
    def test_verify_light_fail(self, mock_run, temp_project_dir):
        (temp_project_dir / "pyproject.toml").write_text('[tool.pytest]\n')
        (temp_project_dir / "tests").mkdir()
        mock_run.return_value = MagicMock(returncode=1, stdout="FAILED", stderr="1 failed")

        v = Verifier(root=temp_project_dir, max_retries=1)
        result = v.verify(tier=VerificationTier.LIGHT)
        assert result.passed is False

    @patch("orchestrator.verify.subprocess.run")
    def test_verify_standard(self, mock_run, temp_project_dir):
        (temp_project_dir / "pyproject.toml").write_text('[tool.pytest]\n')
        (temp_project_dir / "tests").mkdir()
        mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")

        v = Verifier(root=temp_project_dir)
        result = v.verify(tier=VerificationTier.STANDARD)
        # Should have test + typecheck + lint checks
        check_types = [e.check_type for e in result.evidence]
        assert "test" in check_types
        assert "typecheck" in check_types
        assert "lint" in check_types

    @patch("orchestrator.verify.subprocess.run")
    def test_verify_thorough(self, mock_run, temp_project_dir):
        (temp_project_dir / "pyproject.toml").write_text('[tool.pytest]\n')
        (temp_project_dir / "tests").mkdir()
        mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")

        v = Verifier(root=temp_project_dir)
        result = v.verify(tier=VerificationTier.THOROUGH)
        check_types = [e.check_type for e in result.evidence]
        assert "build" in check_types

    @patch("orchestrator.verify.subprocess.run")
    def test_verify_command_not_found(self, mock_run, temp_project_dir):
        (temp_project_dir / "Cargo.toml").write_text('[package]\nname="test"')
        mock_run.side_effect = FileNotFoundError("cargo not found")

        v = Verifier(root=temp_project_dir, max_retries=1)
        result = v.verify(tier=VerificationTier.LIGHT)
        assert result.passed is False

    @patch("orchestrator.verify.subprocess.run")
    def test_verify_timeout(self, mock_run, temp_project_dir):
        (temp_project_dir / "pyproject.toml").write_text('[tool.pytest]\n')
        (temp_project_dir / "tests").mkdir()
        mock_run.side_effect = subprocess.TimeoutExpired("pytest", 300)

        v = Verifier(root=temp_project_dir, max_retries=1)
        result = v.verify(tier=VerificationTier.LIGHT)
        assert result.evidence[0].status == "error"

    def test_verify_unknown_project(self, temp_project_dir):
        v = Verifier(root=temp_project_dir)
        result = v.verify(tier=VerificationTier.LIGHT)
        # Unknown project has no test cmd, should skip
        assert len(result.evidence) > 0

    @patch("orchestrator.verify.subprocess.run")
    def test_verify_retry(self, mock_run, temp_project_dir):
        (temp_project_dir / "pyproject.toml").write_text('[tool.pytest]\n')
        (temp_project_dir / "tests").mkdir()
        # _has_tool calls also go through subprocess.run, so we need to
        # handle both tool-detection calls and the actual test calls.
        call_count = {"n": 0}
        check_results = [
            MagicMock(returncode=1, stdout="FAIL", stderr=""),
            MagicMock(returncode=0, stdout="PASS", stderr=""),
        ]

        def side_effect_fn(cmd, **kwargs):
            if "--version" in cmd:
                raise FileNotFoundError("not found")
            idx = min(call_count["n"], len(check_results) - 1)
            result = check_results[call_count["n"]]
            call_count["n"] += 1
            return result

        mock_run.side_effect = side_effect_fn

        v = Verifier(root=temp_project_dir, max_retries=2)
        result = v.verify(tier=VerificationTier.LIGHT)
        assert result.passed is True
        assert result.retry_count >= 1

    def test_get_checks_for_light(self, temp_project_dir):
        (temp_project_dir / "pyproject.toml").write_text('[tool.pytest]\n')
        v = Verifier(root=temp_project_dir)
        project = v.detector.detect()
        checks = v._get_checks_for_tier(VerificationTier.LIGHT, project)
        check_types = [c[0] for c in checks]
        assert check_types == ["test"]

    def test_get_checks_for_standard(self, temp_project_dir):
        (temp_project_dir / "pyproject.toml").write_text('[tool.pytest]\n')
        v = Verifier(root=temp_project_dir)
        project = v.detector.detect()
        checks = v._get_checks_for_tier(VerificationTier.STANDARD, project)
        check_types = [c[0] for c in checks]
        assert "test" in check_types
        assert "typecheck" in check_types
        assert "lint" in check_types

    def test_get_checks_for_thorough(self, temp_project_dir):
        (temp_project_dir / "pyproject.toml").write_text('[tool.pytest]\n')
        v = Verifier(root=temp_project_dir)
        project = v.detector.detect()
        checks = v._get_checks_for_tier(VerificationTier.THOROUGH, project)
        check_types = [c[0] for c in checks]
        assert "build" in check_types
