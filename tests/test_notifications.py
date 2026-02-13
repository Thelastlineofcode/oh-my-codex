"""Tests for notifications module."""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from orchestrator.notifications import (
    NotificationChannel,
    NotificationLevel,
    NotificationConfig,
    Notification,
    NotificationResult,
    NotificationManager,
)


class TestNotificationChannel:
    def test_values(self):
        assert NotificationChannel.TELEGRAM.value == "telegram"
        assert NotificationChannel.DISCORD.value == "discord"
        assert NotificationChannel.TMUX.value == "tmux"
        assert NotificationChannel.TERMINAL.value == "terminal"


class TestNotificationLevel:
    def test_values(self):
        assert NotificationLevel.SUCCESS.value == "success"
        assert NotificationLevel.ERROR.value == "error"


class TestNotification:
    def test_create(self):
        n = Notification(title="Test", message="Hello")
        assert n.level == NotificationLevel.INFO


class TestNotificationManager:
    def test_add_channel(self):
        mgr = NotificationManager()
        mgr.add_channel(NotificationConfig(channel=NotificationChannel.TERMINAL))
        assert len(mgr.get_channels()) == 1

    def test_remove_channel(self):
        mgr = NotificationManager()
        mgr.add_channel(NotificationConfig(channel=NotificationChannel.TERMINAL))
        assert mgr.remove_channel(NotificationChannel.TERMINAL) is True
        assert len(mgr.get_channels()) == 0

    def test_remove_nonexistent(self):
        mgr = NotificationManager()
        assert mgr.remove_channel(NotificationChannel.TELEGRAM) is False

    def test_notify_terminal(self, capsys):
        mgr = NotificationManager()
        mgr.add_channel(NotificationConfig(channel=NotificationChannel.TERMINAL))
        results = mgr.notify(Notification(title="Test", message="Hello"))
        assert len(results) == 1
        assert results[0].success is True
        captured = capsys.readouterr()
        assert "Test" in captured.out

    def test_notify_disabled_channel(self):
        mgr = NotificationManager()
        mgr.add_channel(NotificationConfig(channel=NotificationChannel.TERMINAL, enabled=False))
        results = mgr.notify(Notification(title="Test", message="Hello"))
        assert len(results) == 0

    def test_notify_session_end_success(self, capsys):
        mgr = NotificationManager()
        mgr.add_channel(NotificationConfig(channel=NotificationChannel.TERMINAL))
        results = mgr.notify_session_end("sess-1", "autopilot", True, "All done")
        assert results[0].success is True

    def test_notify_session_end_failure(self, capsys):
        mgr = NotificationManager()
        mgr.add_channel(NotificationConfig(channel=NotificationChannel.TERMINAL))
        results = mgr.notify_session_end("sess-1", "ralph", False)
        assert results[0].success is True

    def test_notify_error(self, capsys):
        mgr = NotificationManager()
        mgr.add_channel(NotificationConfig(channel=NotificationChannel.TERMINAL))
        results = mgr.notify_error("Something broke", "sess-1")
        assert results[0].success is True

    def test_telegram_missing_config(self):
        mgr = NotificationManager()
        mgr.add_channel(NotificationConfig(channel=NotificationChannel.TELEGRAM))
        results = mgr.notify(Notification(title="T", message="M"))
        assert results[0].success is False
        assert "Missing" in results[0].error

    def test_discord_missing_config(self):
        mgr = NotificationManager()
        mgr.add_channel(NotificationConfig(channel=NotificationChannel.DISCORD))
        results = mgr.notify(Notification(title="T", message="M"))
        assert results[0].success is False

    @patch("orchestrator.notifications.subprocess.run")
    def test_tmux_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        mgr = NotificationManager()
        mgr.add_channel(NotificationConfig(channel=NotificationChannel.TMUX))
        results = mgr.notify(Notification(title="T", message="M"))
        assert results[0].success is True

    @patch("orchestrator.notifications.subprocess.run")
    def test_tmux_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        mgr = NotificationManager()
        mgr.add_channel(NotificationConfig(channel=NotificationChannel.TMUX))
        results = mgr.notify(Notification(title="T", message="M"))
        assert results[0].success is False

    def test_load_config(self):
        tmpdir = tempfile.mkdtemp()
        try:
            path = Path(tmpdir) / "notif.json"
            path.write_text(json.dumps({"notifications": [
                {"channel": "terminal", "enabled": True},
                {"channel": "telegram", "telegram_bot_token": "tok", "telegram_chat_id": "123"},
            ]}))
            mgr = NotificationManager(config_path=path)
            assert len(mgr.get_channels()) == 2
        finally:
            shutil.rmtree(tmpdir)

    def test_load_nonexistent(self):
        mgr = NotificationManager(config_path="/nonexistent/file.json")
        assert len(mgr.get_channels()) == 0

    def test_save_config(self):
        tmpdir = tempfile.mkdtemp()
        try:
            path = Path(tmpdir) / "notif.json"
            mgr = NotificationManager()
            mgr.add_channel(NotificationConfig(
                channel=NotificationChannel.TELEGRAM,
                telegram_bot_token="tok",
                telegram_chat_id="123",
                tags=["@user"],
            ))
            assert mgr.save_config(path) is True
            data = json.loads(path.read_text())
            assert len(data["notifications"]) == 1
            assert data["notifications"][0]["tags"] == ["@user"]
        finally:
            shutil.rmtree(tmpdir)
