"""
HUD (Heads-Up Display) for Oh My Codex.
Real-time status monitor with ANSI rendering and multiple presets.
"""
from __future__ import annotations

import os
import sys
import time
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# Defaults
_HUD_DEFAULT_PRESET = "focused"
_HUD_WATCH_INTERVAL = 2.0  # seconds


class HUDPreset(Enum):
    """HUD display presets."""
    MINIMAL = "minimal"
    FOCUSED = "focused"
    FULL = "full"


class HUDColors:
    """ANSI color codes for HUD rendering."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Mode colors
    CYAN = "\033[36m"       # autopilot
    RED = "\033[31m"        # ralph
    YELLOW = "\033[33m"     # ultrawork
    GREEN = "\033[32m"      # eco
    MAGENTA = "\033[35m"    # ultrapilot
    BLUE = "\033[34m"       # plan
    WHITE = "\033[37m"      # default

    # UI elements
    ORANGE = "\033[38;5;208m"
    GRAY = "\033[38;5;245m"

    # Box drawing
    BOX_H = "─"
    BOX_V = "│"
    BOX_TL = "┌"
    BOX_TR = "┐"
    BOX_BL = "└"
    BOX_BR = "┘"

    MODE_COLORS: dict[str, str] = {
        "autopilot": "\033[36m",   # cyan
        "ralph": "\033[31m",       # red
        "ultrawork": "\033[33m",   # yellow
        "eco": "\033[32m",         # green
        "ultrapilot": "\033[35m",  # magenta
        "plan": "\033[34m",        # blue
        "tdd": "\033[36m",         # cyan
        "review": "\033[33m",      # yellow
        "debug": "\033[31m",       # red
        "pipeline": "\033[34m",    # blue
        "research": "\033[35m",    # magenta
        "deepsearch": "\033[34m",  # blue
        "team": "\033[33m",        # yellow
    }

    @classmethod
    def for_mode(cls, mode: str) -> str:
        """Get color for a mode."""
        return cls.MODE_COLORS.get(mode, cls.WHITE)


@dataclass
class HUDData:
    """Data structure for HUD rendering."""
    mode: str = ""
    phase: str = ""
    iteration: int = 0
    agents: list[str] = field(default_factory=list)
    tokens: dict[str, int] = field(default_factory=dict)
    total_tokens: int = 0
    git_branch: str = ""
    session_id: str = ""
    uptime: str = ""
    started_at: str = ""


class HUDRenderer:
    """ANSI renderer for HUD output."""

    def render(self, data: HUDData, preset: HUDPreset = HUDPreset.FOCUSED) -> str:
        """Render HUD data according to preset."""
        if preset == HUDPreset.MINIMAL:
            return self._render_minimal(data)
        elif preset == HUDPreset.FOCUSED:
            return self._render_focused(data)
        else:
            return self._render_full(data)

    def _render_minimal(self, data: HUDData) -> str:
        """Single-line minimal output."""
        if not data.mode:
            return f"{HUDColors.DIM}No active mode{HUDColors.RESET}"

        color = HUDColors.for_mode(data.mode)
        parts = [
            f"{color}{HUDColors.BOLD}[{data.mode.upper()}]{HUDColors.RESET}",
            f"{data.phase}",
        ]

        if data.iteration > 0:
            parts.append(f"(iter {data.iteration})")

        if data.agents:
            parts.append(f"| {len(data.agents)} agents")

        if data.total_tokens > 0:
            parts.append(f"| {self._format_tokens(data.total_tokens)} tokens")

        return " ".join(parts)

    def _render_focused(self, data: HUDData) -> str:
        """Box-style focused output."""
        if not data.mode:
            return self._box("OMX HUD", [f"{HUDColors.DIM}No active mode{HUDColors.RESET}"])

        color = HUDColors.for_mode(data.mode)
        lines = []

        # Mode + phase
        mode_line = f"  {color}{HUDColors.BOLD}{data.mode.upper()}{HUDColors.RESET}"
        mode_line += f"  {HUDColors.DIM}{data.phase}{HUDColors.RESET}"
        if data.iteration > 0:
            mode_line += f"  {HUDColors.DIM}iter {data.iteration}{HUDColors.RESET}"
        lines.append(mode_line)
        lines.append("")

        # Agents
        if data.agents:
            lines.append(f"  {HUDColors.BOLD}Agents:{HUDColors.RESET} {', '.join(data.agents)}")

        # Tokens
        if data.total_tokens > 0:
            lines.append(f"  {HUDColors.BOLD}Tokens:{HUDColors.RESET} {self._format_tokens(data.total_tokens)}")
            if data.tokens:
                for role, count in data.tokens.items():
                    lines.append(f"    {HUDColors.DIM}{role}: {self._format_tokens(count)}{HUDColors.RESET}")

        # Uptime
        if data.uptime:
            lines.append(f"  {HUDColors.BOLD}Uptime:{HUDColors.RESET} {data.uptime}")

        return self._box("OMX HUD", lines)

    def _render_full(self, data: HUDData) -> str:
        """Full dashboard output."""
        if not data.mode:
            return self._box("OMX HUD - Full Dashboard", [f"{HUDColors.DIM}No active mode{HUDColors.RESET}"])

        color = HUDColors.for_mode(data.mode)
        lines = []

        # Header
        mode_line = f"  {color}{HUDColors.BOLD}{data.mode.upper()}{HUDColors.RESET}"
        mode_line += f"  {data.phase}"
        if data.iteration > 0:
            mode_line += f"  (iteration {data.iteration})"
        lines.append(mode_line)
        lines.append(f"  {HUDColors.GRAY}{'─' * 40}{HUDColors.RESET}")

        # Session
        if data.session_id:
            lines.append(f"  {HUDColors.BOLD}Session:{HUDColors.RESET}  {data.session_id}")

        # Git
        if data.git_branch:
            lines.append(f"  {HUDColors.BOLD}Branch:{HUDColors.RESET}   {data.git_branch}")

        # Uptime
        if data.uptime:
            lines.append(f"  {HUDColors.BOLD}Uptime:{HUDColors.RESET}   {data.uptime}")

        if data.started_at:
            lines.append(f"  {HUDColors.BOLD}Started:{HUDColors.RESET}  {data.started_at}")

        lines.append(f"  {HUDColors.GRAY}{'─' * 40}{HUDColors.RESET}")

        # Agents detail
        lines.append(f"  {HUDColors.BOLD}Agents ({len(data.agents)}):{HUDColors.RESET}")
        if data.agents:
            for agent in data.agents:
                token_info = ""
                if agent in data.tokens:
                    token_info = f" ({self._format_tokens(data.tokens[agent])} tokens)"
                lines.append(f"    {HUDColors.GREEN}●{HUDColors.RESET} {agent}{HUDColors.DIM}{token_info}{HUDColors.RESET}")
        else:
            lines.append(f"    {HUDColors.DIM}None active{HUDColors.RESET}")

        lines.append(f"  {HUDColors.GRAY}{'─' * 40}{HUDColors.RESET}")

        # Token summary
        lines.append(f"  {HUDColors.BOLD}Tokens:{HUDColors.RESET}   {self._format_tokens(data.total_tokens)} total")
        if data.tokens:
            for role, count in sorted(data.tokens.items(), key=lambda x: x[1], reverse=True):
                pct = (count / data.total_tokens * 100) if data.total_tokens > 0 else 0
                bar = self._progress_bar(pct, 15)
                lines.append(f"    {role:<12} {bar} {self._format_tokens(count)} ({pct:.0f}%)")

        return self._box("OMX HUD - Full Dashboard", lines)

    def _box(self, title: str, lines: list[str]) -> str:
        """Render a box around content."""
        c = HUDColors
        width = 50

        result = []
        result.append(f"  {c.GRAY}{c.BOX_TL}{'─' * (width - 2)}{c.BOX_TR}{c.RESET}")
        result.append(f"  {c.GRAY}{c.BOX_V}{c.RESET} {c.ORANGE}{c.BOLD}{title}{c.RESET}{' ' * (width - len(title) - 4)}{c.GRAY}{c.BOX_V}{c.RESET}")
        result.append(f"  {c.GRAY}{c.BOX_V}{'─' * (width - 2)}{c.BOX_V}{c.RESET}")

        for line in lines:
            result.append(f"  {c.GRAY}{c.BOX_V}{c.RESET}{line}")

        result.append(f"  {c.GRAY}{c.BOX_BL}{'─' * (width - 2)}{c.BOX_BR}{c.RESET}")

        return "\n".join(result)

    def _format_tokens(self, count: int) -> str:
        """Format token count for display."""
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K"
        return str(count)

    def _progress_bar(self, pct: float, width: int = 15) -> str:
        """Render a simple progress bar."""
        filled = int(pct / 100 * width)
        empty = width - filled
        return f"{HUDColors.GREEN}{'█' * filled}{HUDColors.DIM}{'░' * empty}{HUDColors.RESET}"


class HUD:
    """Main HUD controller."""

    def __init__(self, state_manager: Any = None) -> None:
        """Initialize HUD with optional StateManager."""
        self._state_manager = state_manager
        self._renderer = HUDRenderer()

    def _get_git_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass
        return ""

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable form."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            m = int(seconds // 60)
            s = int(seconds % 60)
            return f"{m}m {s}s"
        else:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            return f"{h}h {m}m"

    def _collect_data(self) -> HUDData:
        """Collect HUD data from state manager."""
        data = HUDData()

        if self._state_manager is None:
            return data

        snapshot = self._state_manager.get_snapshot()
        data.mode = snapshot.mode
        data.phase = snapshot.phase
        data.iteration = snapshot.iteration
        data.agents = snapshot.active_agents
        data.session_id = snapshot.session_id
        data.started_at = snapshot.started_at
        data.total_tokens = snapshot.total_tokens

        # Get token breakdown
        if snapshot.session_id:
            data.tokens = self._state_manager.get_token_breakdown(snapshot.session_id)

        # Git branch
        data.git_branch = self._get_git_branch()

        # Uptime
        if snapshot.uptime_seconds > 0:
            data.uptime = self._format_uptime(snapshot.uptime_seconds)

        return data

    def show(self, preset: str | HUDPreset = _HUD_DEFAULT_PRESET) -> str:
        """Show HUD once and return the rendered string."""
        if isinstance(preset, str):
            try:
                preset = HUDPreset(preset)
            except ValueError:
                preset = HUDPreset.FOCUSED

        data = self._collect_data()
        output = self._renderer.render(data, preset)
        print(output)
        return output

    def watch(self, preset: str | HUDPreset = _HUD_DEFAULT_PRESET, interval: float = _HUD_WATCH_INTERVAL) -> None:
        """Watch HUD with live refresh. Press Ctrl+C to stop."""
        if isinstance(preset, str):
            try:
                preset = HUDPreset(preset)
            except ValueError:
                preset = HUDPreset.FOCUSED

        try:
            while True:
                # Clear screen
                os.system("clear" if os.name == "posix" else "cls")
                data = self._collect_data()
                output = self._renderer.render(data, preset)
                print(output)
                print(f"\n  {HUDColors.DIM}Press Ctrl+C to stop{HUDColors.RESET}")
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n  {HUDColors.DIM}HUD stopped.{HUDColors.RESET}")

    def render_string(self, preset: str | HUDPreset = _HUD_DEFAULT_PRESET) -> str:
        """Render HUD to string without printing."""
        if isinstance(preset, str):
            try:
                preset = HUDPreset(preset)
            except ValueError:
                preset = HUDPreset.FOCUSED

        data = self._collect_data()
        return self._renderer.render(data, preset)
