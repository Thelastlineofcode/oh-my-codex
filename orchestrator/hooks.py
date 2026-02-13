"""
Lifecycle hook system for Oh My Codex.
Event-based hooks for task execution, session management, and mode changes.
"""
from __future__ import annotations

import json
import logging
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


class HookEvent(Enum):
    """Lifecycle events that can trigger hooks."""
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    MODE_START = "mode_start"
    MODE_END = "mode_end"
    TASK_START = "task_start"
    TASK_END = "task_end"
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    VERIFY_START = "verify_start"
    VERIFY_END = "verify_end"
    ERROR = "error"
    PHASE_CHANGE = "phase_change"


@dataclass
class HookConfig:
    """Configuration for a single hook."""
    event: HookEvent
    command: str = ""
    script: str = ""
    callback: Callable[..., Any] | None = None
    enabled: bool = True
    timeout: int = 30
    name: str = ""


@dataclass
class HookResult:
    """Result of a hook execution."""
    event: HookEvent
    hook_name: str
    success: bool
    output: str = ""
    duration: float = 0.0
    error: str = ""


@dataclass
class HookContext:
    """Context passed to hooks."""
    event: HookEvent
    session_id: str = ""
    mode: str = ""
    phase: str = ""
    task: str = ""
    agent_role: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def to_env(self) -> dict[str, str]:
        """Convert to environment variables for shell hooks."""
        env = {
            "OMX_EVENT": self.event.value,
            "OMX_SESSION_ID": self.session_id,
            "OMX_MODE": self.mode,
            "OMX_PHASE": self.phase,
            "OMX_TASK": self.task,
            "OMX_AGENT": self.agent_role,
        }
        for k, v in self.data.items():
            env[f"OMX_DATA_{k.upper()}"] = str(v)
        return env


class HookManager:
    """Manages lifecycle hooks registration and execution."""

    def __init__(self) -> None:
        self._hooks: dict[HookEvent, list[HookConfig]] = {}
        self._results: list[HookResult] = []

    def register(self, hook: HookConfig) -> None:
        """Register a hook for an event."""
        if hook.event not in self._hooks:
            self._hooks[hook.event] = []
        self._hooks[hook.event].append(hook)

    def unregister(self, event: HookEvent, name: str) -> bool:
        """Unregister a named hook."""
        if event not in self._hooks:
            return False
        before = len(self._hooks[event])
        self._hooks[event] = [h for h in self._hooks[event] if h.name != name]
        return len(self._hooks[event]) < before

    def on(self, event: HookEvent, command: str = "", callback: Callable[..., Any] | None = None, name: str = "", timeout: int = 30) -> None:
        """Convenience method to register a hook."""
        hook = HookConfig(
            event=event,
            command=command,
            callback=callback,
            name=name or f"{event.value}_{len(self._hooks.get(event, []))}",
            timeout=timeout,
        )
        self.register(hook)

    def emit(self, context: HookContext) -> list[HookResult]:
        """Emit an event and execute all registered hooks."""
        hooks = self._hooks.get(context.event, [])
        results = []

        for hook in hooks:
            if not hook.enabled:
                continue
            result = self._execute_hook(hook, context)
            results.append(result)
            self._results.append(result)

        return results

    def _execute_hook(self, hook: HookConfig, context: HookContext) -> HookResult:
        """Execute a single hook."""
        start = time.monotonic()
        name = hook.name or hook.event.value

        # Python callback
        if hook.callback:
            try:
                output = hook.callback(context)
                duration = time.monotonic() - start
                return HookResult(
                    event=context.event,
                    hook_name=name,
                    success=True,
                    output=str(output) if output else "",
                    duration=duration,
                )
            except Exception as e:
                duration = time.monotonic() - start
                return HookResult(
                    event=context.event,
                    hook_name=name,
                    success=False,
                    error=str(e),
                    duration=duration,
                )

        # Shell command
        if hook.command:
            try:
                env = {**dict(__import__("os").environ), **context.to_env()}
                result = subprocess.run(
                    hook.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=hook.timeout,
                    env=env,
                )
                duration = time.monotonic() - start
                return HookResult(
                    event=context.event,
                    hook_name=name,
                    success=result.returncode == 0,
                    output=result.stdout.strip(),
                    error=result.stderr.strip() if result.returncode != 0 else "",
                    duration=duration,
                )
            except subprocess.TimeoutExpired:
                duration = time.monotonic() - start
                return HookResult(
                    event=context.event,
                    hook_name=name,
                    success=False,
                    error=f"Hook timed out after {hook.timeout}s",
                    duration=duration,
                )
            except Exception as e:
                duration = time.monotonic() - start
                return HookResult(
                    event=context.event,
                    hook_name=name,
                    success=False,
                    error=str(e),
                    duration=duration,
                )

        return HookResult(
            event=context.event,
            hook_name=name,
            success=True,
            output="No action configured",
            duration=0.0,
        )

    def get_hooks(self, event: HookEvent | None = None) -> list[HookConfig]:
        """Get registered hooks, optionally filtered by event."""
        if event:
            return self._hooks.get(event, [])
        return [h for hooks in self._hooks.values() for h in hooks]

    def get_results(self, event: HookEvent | None = None) -> list[HookResult]:
        """Get hook execution results."""
        if event:
            return [r for r in self._results if r.event == event]
        return list(self._results)

    def clear_results(self) -> None:
        """Clear execution history."""
        self._results.clear()

    def load_from_config(self, config_path: str | Path) -> int:
        """Load hooks from a JSON/YAML config file."""
        path = Path(config_path)
        if not path.exists():
            return 0

        try:
            content = path.read_text()
            if path.suffix in (".yaml", ".yml"):
                try:
                    import yaml
                    data = yaml.safe_load(content) or {}
                except ImportError:
                    return 0
            else:
                data = json.loads(content)

            hooks_data = data.get("hooks", [])
            count = 0
            for h in hooks_data:
                try:
                    event = HookEvent(h["event"])
                    hook = HookConfig(
                        event=event,
                        command=h.get("command", ""),
                        name=h.get("name", ""),
                        timeout=h.get("timeout", 30),
                        enabled=h.get("enabled", True),
                    )
                    self.register(hook)
                    count += 1
                except (KeyError, ValueError):
                    continue
            return count
        except Exception:
            return 0

    def save_to_config(self, config_path: str | Path) -> bool:
        """Save hooks to a JSON config file."""
        path = Path(config_path)
        try:
            hooks_data = []
            for event, hooks in self._hooks.items():
                for h in hooks:
                    if h.command:  # Only save shell hooks
                        hooks_data.append({
                            "event": h.event.value,
                            "command": h.command,
                            "name": h.name,
                            "timeout": h.timeout,
                            "enabled": h.enabled,
                        })
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"hooks": hooks_data}, indent=2))
            return True
        except Exception:
            return False
