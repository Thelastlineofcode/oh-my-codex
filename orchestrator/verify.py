"""
Verification protocol for Oh My Codex.
Evidence-backed verification with tiered checks and auto project detection.
"""
from __future__ import annotations

import subprocess
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


# Defaults
_VERIFY_MAX_RETRIES = 3
_VERIFY_SKIP_MODES = {"plan", "eco", "research", "deepsearch"}


class VerificationTier(Enum):
    """Verification tiers based on change scope."""
    LIGHT = "light"
    STANDARD = "standard"
    THOROUGH = "thorough"


@dataclass
class Evidence:
    """A single piece of verification evidence."""
    check_type: str  # test, typecheck, lint, build
    command: str
    status: str  # pass, fail, skip, error
    output: str = ""
    duration: float = 0.0


@dataclass
class VerificationResult:
    """Result of a verification run."""
    tier: VerificationTier
    passed: bool
    evidence: list[Evidence] = field(default_factory=list)
    confidence: float = 0.0
    retry_count: int = 0
    summary: str = ""


@dataclass
class ProjectConfig:
    """Detected project configuration."""
    project_type: str  # python, node, rust, go, unknown
    test_cmd: list[str] = field(default_factory=list)
    typecheck_cmd: list[str] = field(default_factory=list)
    lint_cmd: list[str] = field(default_factory=list)
    build_cmd: list[str] = field(default_factory=list)
    root: str = "."


class ProjectDetector:
    """Auto-detect project type and available commands."""

    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def detect(self) -> ProjectConfig:
        """Detect project type and available commands."""
        # Python
        if (self.root / "pyproject.toml").exists() or (self.root / "setup.py").exists():
            return self._detect_python()
        # Node.js
        if (self.root / "package.json").exists():
            return self._detect_node()
        # Rust
        if (self.root / "Cargo.toml").exists():
            return self._detect_rust()
        # Go
        if (self.root / "go.mod").exists():
            return self._detect_go()

        return ProjectConfig(project_type="unknown", root=str(self.root))

    def _detect_python(self) -> ProjectConfig:
        """Detect Python project configuration."""
        config = ProjectConfig(project_type="python", root=str(self.root))

        # Test command
        if (self.root / "pyproject.toml").exists():
            content = (self.root / "pyproject.toml").read_text()
            if "pytest" in content:
                config.test_cmd = ["pytest"]
            elif (self.root / "tests").exists():
                config.test_cmd = ["pytest"]
            else:
                config.test_cmd = ["python", "-m", "pytest"]
        else:
            config.test_cmd = ["python", "-m", "pytest"]

        # Type checking
        if self._has_tool("mypy"):
            config.typecheck_cmd = ["mypy", "."]
        elif self._has_tool("pyright"):
            config.typecheck_cmd = ["pyright"]

        # Linting
        if self._has_tool("ruff"):
            config.lint_cmd = ["ruff", "check", "."]
        elif self._has_tool("flake8"):
            config.lint_cmd = ["flake8", "."]

        # Build
        config.build_cmd = ["python", "-m", "build"]

        return config

    def _detect_node(self) -> ProjectConfig:
        """Detect Node.js project configuration."""
        config = ProjectConfig(project_type="node", root=str(self.root))

        import json
        try:
            pkg = json.loads((self.root / "package.json").read_text())
            scripts = pkg.get("scripts", {})
        except (json.JSONDecodeError, OSError):
            scripts = {}

        # Test
        if "test" in scripts:
            config.test_cmd = ["npm", "test"]

        # Type checking
        if (self.root / "tsconfig.json").exists():
            config.typecheck_cmd = ["npx", "tsc", "--noEmit"]

        # Linting
        if "lint" in scripts:
            config.lint_cmd = ["npm", "run", "lint"]
        elif (self.root / ".eslintrc.json").exists() or (self.root / ".eslintrc.js").exists():
            config.lint_cmd = ["npx", "eslint", "."]

        # Build
        if "build" in scripts:
            config.build_cmd = ["npm", "run", "build"]

        return config

    def _detect_rust(self) -> ProjectConfig:
        """Detect Rust project configuration."""
        return ProjectConfig(
            project_type="rust",
            root=str(self.root),
            test_cmd=["cargo", "test"],
            typecheck_cmd=["cargo", "check"],
            lint_cmd=["cargo", "clippy"],
            build_cmd=["cargo", "build"],
        )

    def _detect_go(self) -> ProjectConfig:
        """Detect Go project configuration."""
        config = ProjectConfig(project_type="go", root=str(self.root))
        config.test_cmd = ["go", "test", "./..."]
        config.build_cmd = ["go", "build", "./..."]

        if self._has_tool("golangci-lint"):
            config.lint_cmd = ["golangci-lint", "run"]

        return config

    def _has_tool(self, name: str) -> bool:
        """Check if a tool is available on PATH."""
        try:
            subprocess.run(
                [name, "--version"],
                capture_output=True,
                timeout=5,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return False


class Verifier:
    """Execute verification checks with evidence collection."""

    def __init__(self, root: str | Path = ".", max_retries: int | None = None) -> None:
        self.root = Path(root)
        self.max_retries = max_retries if max_retries is not None else _VERIFY_MAX_RETRIES
        self.detector = ProjectDetector(self.root)

    def classify_tier(self, files_changed: int = 0, lines_changed: int = 0) -> VerificationTier:
        """Classify verification tier based on change scope."""
        if files_changed <= 3 and lines_changed < 100:
            return VerificationTier.LIGHT
        elif files_changed <= 15 and lines_changed < 500:
            return VerificationTier.STANDARD
        else:
            return VerificationTier.THOROUGH

    def verify(
        self,
        tier: VerificationTier | None = None,
        files_changed: int = 0,
        lines_changed: int = 0,
        mode: str = "",
    ) -> VerificationResult:
        """Run verification checks based on tier."""
        # Skip for certain modes
        if mode in _VERIFY_SKIP_MODES:
            return VerificationResult(
                tier=tier or VerificationTier.LIGHT,
                passed=True,
                evidence=[Evidence(check_type="skip", command="", status="skip", output=f"Skipped for mode: {mode}")],
                confidence=1.0,
                summary=f"Verification skipped for {mode} mode",
            )

        effective_tier = tier or self.classify_tier(files_changed, lines_changed)
        project = self.detector.detect()

        # Determine which checks to run based on tier
        checks = self._get_checks_for_tier(effective_tier, project)

        all_evidence: list[Evidence] = []
        all_passed = True
        retry_count = 0

        for check_type, cmd in checks:
            if not cmd:
                all_evidence.append(Evidence(
                    check_type=check_type, command="", status="skip",
                    output=f"No {check_type} command configured",
                ))
                continue

            passed = False
            for attempt in range(self.max_retries):
                evidence = self._run_check(check_type, cmd)
                all_evidence.append(evidence)

                if evidence.status == "pass":
                    passed = True
                    break
                retry_count += 1

            if not passed:
                all_passed = False

        # Calculate confidence
        total_checks = len([e for e in all_evidence if e.status != "skip"])
        passed_checks = len([e for e in all_evidence if e.status == "pass"])
        confidence = passed_checks / total_checks if total_checks > 0 else 1.0

        # Build summary
        summary_parts = []
        for e in all_evidence:
            if e.status != "skip":
                icon = "PASS" if e.status == "pass" else "FAIL"
                summary_parts.append(f"[{icon}] {e.check_type}")
        summary = " | ".join(summary_parts) if summary_parts else "No checks run"

        return VerificationResult(
            tier=effective_tier,
            passed=all_passed,
            evidence=all_evidence,
            confidence=confidence,
            retry_count=retry_count,
            summary=summary,
        )

    def _get_checks_for_tier(
        self, tier: VerificationTier, project: ProjectConfig
    ) -> list[tuple[str, list[str]]]:
        """Get the checks to run for a given tier."""
        checks: list[tuple[str, list[str]]] = []

        # All tiers: test
        checks.append(("test", project.test_cmd))

        if tier in (VerificationTier.STANDARD, VerificationTier.THOROUGH):
            checks.append(("typecheck", project.typecheck_cmd))
            checks.append(("lint", project.lint_cmd))

        if tier == VerificationTier.THOROUGH:
            checks.append(("build", project.build_cmd))

        return checks

    def _run_check(self, check_type: str, cmd: list[str]) -> Evidence:
        """Run a single verification check."""
        start = time.monotonic()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(self.root),
            )
            duration = time.monotonic() - start

            status = "pass" if result.returncode == 0 else "fail"
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            # Truncate long output
            if len(output) > 5000:
                output = output[:5000] + "\n... (truncated)"

            return Evidence(
                check_type=check_type,
                command=" ".join(cmd),
                status=status,
                output=output.strip(),
                duration=duration,
            )
        except subprocess.TimeoutExpired:
            duration = time.monotonic() - start
            return Evidence(
                check_type=check_type,
                command=" ".join(cmd),
                status="error",
                output="Command timed out after 300s",
                duration=duration,
            )
        except FileNotFoundError:
            return Evidence(
                check_type=check_type,
                command=" ".join(cmd),
                status="error",
                output=f"Command not found: {cmd[0]}",
                duration=0.0,
            )
        except Exception as e:
            duration = time.monotonic() - start
            return Evidence(
                check_type=check_type,
                command=" ".join(cmd),
                status="error",
                output=str(e),
                duration=duration,
            )
