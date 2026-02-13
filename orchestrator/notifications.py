"""
Notification system for Oh My Codex.
Supports Telegram, Discord webhooks, and terminal (tmux) notifications.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    TELEGRAM = "telegram"
    DISCORD = "discord"
    TMUX = "tmux"
    TERMINAL = "terminal"


class NotificationLevel(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class NotificationConfig:
    """Configuration for a notification channel."""
    channel: NotificationChannel
    enabled: bool = True
    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    # Discord
    discord_webhook_url: str = ""
    # Tags
    tags: list[str] = field(default_factory=list)


@dataclass
class Notification:
    """A notification message."""
    title: str
    message: str
    level: NotificationLevel = NotificationLevel.INFO
    session_id: str = ""
    mode: str = ""
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationResult:
    """Result of sending a notification."""
    channel: NotificationChannel
    success: bool
    error: str = ""


class NotificationManager:
    """Manages notification channels and dispatching."""

    def __init__(self, config_path: str | Path | None = None) -> None:
        self._channels: list[NotificationConfig] = []
        if config_path:
            self.load_config(config_path)

    def add_channel(self, config: NotificationConfig) -> None:
        """Add a notification channel."""
        self._channels.append(config)

    def remove_channel(self, channel: NotificationChannel) -> bool:
        """Remove a notification channel."""
        before = len(self._channels)
        self._channels = [c for c in self._channels if c.channel != channel]
        return len(self._channels) < before

    def get_channels(self) -> list[NotificationConfig]:
        """Get all configured channels."""
        return list(self._channels)

    def notify(self, notification: Notification) -> list[NotificationResult]:
        """Send notification to all enabled channels."""
        results = []
        for config in self._channels:
            if not config.enabled:
                continue
            result = self._send(config, notification)
            results.append(result)
        return results

    def notify_session_end(self, session_id: str, mode: str, success: bool, summary: str = "") -> list[NotificationResult]:
        """Convenience: notify session completion."""
        level = NotificationLevel.SUCCESS if success else NotificationLevel.ERROR
        icon = "✅" if success else "❌"
        title = f"{icon} OMX Session Complete"
        message = f"Mode: {mode}\nSession: {session_id}\nStatus: {'Success' if success else 'Failed'}"
        if summary:
            message += f"\n{summary}"
        return self.notify(Notification(title=title, message=message, level=level, session_id=session_id, mode=mode))

    def notify_error(self, error: str, session_id: str = "", mode: str = "") -> list[NotificationResult]:
        """Convenience: notify error."""
        return self.notify(Notification(
            title="❌ OMX Error",
            message=error,
            level=NotificationLevel.ERROR,
            session_id=session_id,
            mode=mode,
        ))

    def _send(self, config: NotificationConfig, notification: Notification) -> NotificationResult:
        """Send to a specific channel."""
        try:
            if config.channel == NotificationChannel.TELEGRAM:
                return self._send_telegram(config, notification)
            elif config.channel == NotificationChannel.DISCORD:
                return self._send_discord(config, notification)
            elif config.channel == NotificationChannel.TMUX:
                return self._send_tmux(config, notification)
            elif config.channel == NotificationChannel.TERMINAL:
                return self._send_terminal(config, notification)
            return NotificationResult(channel=config.channel, success=False, error="Unknown channel")
        except Exception as e:
            return NotificationResult(channel=config.channel, success=False, error=str(e))

    def _send_telegram(self, config: NotificationConfig, notification: Notification) -> NotificationResult:
        """Send via Telegram Bot API."""
        if not config.telegram_bot_token or not config.telegram_chat_id:
            return NotificationResult(channel=NotificationChannel.TELEGRAM, success=False, error="Missing bot_token or chat_id")

        tag_prefix = " ".join(config.tags) + " " if config.tags else ""
        text = f"{tag_prefix}*{notification.title}*\n{notification.message}"

        url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
        payload = json.dumps({
            "chat_id": config.telegram_chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }).encode()

        try:
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return NotificationResult(channel=NotificationChannel.TELEGRAM, success=True)
                return NotificationResult(channel=NotificationChannel.TELEGRAM, success=False, error=f"HTTP {resp.status}")
        except urllib.error.URLError as e:
            return NotificationResult(channel=NotificationChannel.TELEGRAM, success=False, error=str(e))

    def _send_discord(self, config: NotificationConfig, notification: Notification) -> NotificationResult:
        """Send via Discord webhook."""
        if not config.discord_webhook_url:
            return NotificationResult(channel=NotificationChannel.DISCORD, success=False, error="Missing webhook_url")

        tag_prefix = " ".join(config.tags) + " " if config.tags else ""
        level_color = {
            NotificationLevel.INFO: 3447003,
            NotificationLevel.SUCCESS: 3066993,
            NotificationLevel.WARNING: 15105570,
            NotificationLevel.ERROR: 15158332,
        }

        payload = json.dumps({
            "content": tag_prefix.strip() if tag_prefix.strip() else None,
            "embeds": [{
                "title": notification.title,
                "description": notification.message,
                "color": level_color.get(notification.level, 3447003),
            }],
        }).encode()

        try:
            req = urllib.request.Request(config.discord_webhook_url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (200, 204):
                    return NotificationResult(channel=NotificationChannel.DISCORD, success=True)
                return NotificationResult(channel=NotificationChannel.DISCORD, success=False, error=f"HTTP {resp.status}")
        except urllib.error.URLError as e:
            return NotificationResult(channel=NotificationChannel.DISCORD, success=False, error=str(e))

    def _send_tmux(self, config: NotificationConfig, notification: Notification) -> NotificationResult:
        """Send via tmux display-message."""
        try:
            msg = f"[OMX] {notification.title}: {notification.message[:80]}"
            result = subprocess.run(
                ["tmux", "display-message", msg],
                capture_output=True, text=True, timeout=5,
            )
            return NotificationResult(
                channel=NotificationChannel.TMUX,
                success=result.returncode == 0,
                error=result.stderr.strip() if result.returncode != 0 else "",
            )
        except FileNotFoundError:
            return NotificationResult(channel=NotificationChannel.TMUX, success=False, error="tmux not found")
        except subprocess.TimeoutExpired:
            return NotificationResult(channel=NotificationChannel.TMUX, success=False, error="tmux timeout")

    def _send_terminal(self, config: NotificationConfig, notification: Notification) -> NotificationResult:
        """Send via terminal bell/print."""
        icon = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}.get(notification.level.value, "")
        print(f"\n  {icon} {notification.title}: {notification.message}")
        print("\a", end="", flush=True)  # Terminal bell
        return NotificationResult(channel=NotificationChannel.TERMINAL, success=True)

    def load_config(self, config_path: str | Path) -> int:
        """Load notification config from JSON file."""
        path = Path(config_path)
        if not path.exists():
            return 0
        try:
            data = json.loads(path.read_text())
            channels = data.get("notifications", [])
            count = 0
            for ch in channels:
                try:
                    config = NotificationConfig(
                        channel=NotificationChannel(ch["channel"]),
                        enabled=ch.get("enabled", True),
                        telegram_bot_token=ch.get("telegram_bot_token", ""),
                        telegram_chat_id=ch.get("telegram_chat_id", ""),
                        discord_webhook_url=ch.get("discord_webhook_url", ""),
                        tags=ch.get("tags", []),
                    )
                    self.add_channel(config)
                    count += 1
                except (KeyError, ValueError):
                    continue
            return count
        except Exception:
            return 0

    def save_config(self, config_path: str | Path) -> bool:
        """Save notification config to JSON file."""
        path = Path(config_path)
        try:
            channels = []
            for c in self._channels:
                ch: dict[str, Any] = {"channel": c.channel.value, "enabled": c.enabled}
                if c.telegram_bot_token:
                    ch["telegram_bot_token"] = c.telegram_bot_token
                if c.telegram_chat_id:
                    ch["telegram_chat_id"] = c.telegram_chat_id
                if c.discord_webhook_url:
                    ch["discord_webhook_url"] = c.discord_webhook_url
                if c.tags:
                    ch["tags"] = c.tags
                channels.append(ch)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"notifications": channels}, indent=2))
            return True
        except Exception:
            return False
