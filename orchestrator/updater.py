"""
Auto-update system for Oh My Codex.
PyPI version checking and update management.
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Any


@dataclass
class VersionInfo:
    """Version comparison info."""
    current: str
    latest: str
    update_available: bool
    changelog_url: str = ""


class Updater:
    """Manages version checking and updates."""

    PACKAGE_NAME = "oh-my-codex"
    PYPI_URL = "https://pypi.org/pypi/oh-my-codex/json"
    REPO_URL = "https://github.com/junghwaYang/oh-my-codex"

    def __init__(self, current_version: str | None = None) -> None:
        if current_version:
            self._current = current_version
        else:
            try:
                from orchestrator import __version__
                self._current = __version__
            except ImportError:
                self._current = "0.0.0"

    @property
    def current_version(self) -> str:
        return self._current

    def check_update(self) -> VersionInfo:
        """Check PyPI for latest version."""
        try:
            req = urllib.request.Request(self.PYPI_URL, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                latest = data.get("info", {}).get("version", "0.0.0")
                update_available = self._compare_versions(self._current, latest)
                return VersionInfo(
                    current=self._current,
                    latest=latest,
                    update_available=update_available,
                    changelog_url=f"{self.REPO_URL}/releases",
                )
        except (urllib.error.URLError, json.JSONDecodeError, OSError, KeyError):
            return VersionInfo(
                current=self._current,
                latest="unknown",
                update_available=False,
            )

    def update(self, force: bool = False) -> tuple[bool, str]:
        """Update to latest version via pip."""
        if not force:
            info = self.check_update()
            if not info.update_available:
                return False, f"Already up to date (v{self._current})"

        try:
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", self.PACKAGE_NAME]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                return True, f"Updated successfully. Restart omx to use the new version."
            return False, f"Update failed: {result.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return False, "Update timed out"
        except Exception as e:
            return False, f"Update error: {e}"

    def _compare_versions(self, current: str, latest: str) -> bool:
        """Compare version strings. Returns True if latest > current."""
        try:
            c_parts = [int(x) for x in current.split(".")]
            l_parts = [int(x) for x in latest.split(".")]
            # Pad to same length
            while len(c_parts) < len(l_parts):
                c_parts.append(0)
            while len(l_parts) < len(c_parts):
                l_parts.append(0)
            return l_parts > c_parts
        except (ValueError, AttributeError):
            return False

    def format_update_notice(self) -> str:
        """Format update notification for display."""
        info = self.check_update()
        if not info.update_available:
            return ""
        return (
            f"\n  \033[33m⬆ Update available: v{info.current} → v{info.latest}\033[0m"
            f"\n  \033[2mRun: pip install --upgrade {self.PACKAGE_NAME}\033[0m\n"
        )
