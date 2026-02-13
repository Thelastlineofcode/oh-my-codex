"""Tests for hooks module."""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from orchestrator.hooks import (
    HookEvent,
    HookConfig,
    HookResult,
    HookContext,
    HookManager,
)


class TestHookEvent:
    def test_event_values(self):
        assert HookEvent.SESSION_START.value == "session_start"
        assert HookEvent.TASK_END.value == "task_end"
        assert HookEvent.ERROR.value == "error"


class TestHookContext:
    def test_to_env(self):
        ctx = HookContext(
            event=HookEvent.TASK_START,
            session_id="sess-1",
            mode="autopilot",
            task="test task",
        )
        env = ctx.to_env()
        assert env["OMX_EVENT"] == "task_start"
        assert env["OMX_SESSION_ID"] == "sess-1"
        assert env["OMX_MODE"] == "autopilot"

    def test_to_env_with_data(self):
        ctx = HookContext(
            event=HookEvent.ERROR,
            data={"code": "42", "msg": "fail"},
        )
        env = ctx.to_env()
        assert env["OMX_DATA_CODE"] == "42"
        assert env["OMX_DATA_MSG"] == "fail"


class TestHookManager:
    def test_register_hook(self):
        mgr = HookManager()
        hook = HookConfig(event=HookEvent.SESSION_START, command="echo hi", name="test")
        mgr.register(hook)
        assert len(mgr.get_hooks(HookEvent.SESSION_START)) == 1

    def test_unregister_hook(self):
        mgr = HookManager()
        mgr.on(HookEvent.SESSION_START, command="echo hi", name="test")
        assert mgr.unregister(HookEvent.SESSION_START, "test") is True
        assert len(mgr.get_hooks(HookEvent.SESSION_START)) == 0

    def test_unregister_nonexistent(self):
        mgr = HookManager()
        assert mgr.unregister(HookEvent.SESSION_START, "nope") is False

    def test_on_convenience(self):
        mgr = HookManager()
        mgr.on(HookEvent.TASK_START, command="echo start")
        hooks = mgr.get_hooks(HookEvent.TASK_START)
        assert len(hooks) == 1

    def test_emit_callback(self):
        mgr = HookManager()
        called = []
        def my_hook(ctx):
            called.append(ctx.event)
            return "ok"
        mgr.on(HookEvent.SESSION_START, callback=my_hook, name="cb")
        ctx = HookContext(event=HookEvent.SESSION_START)
        results = mgr.emit(ctx)
        assert len(results) == 1
        assert results[0].success is True
        assert called == [HookEvent.SESSION_START]

    def test_emit_callback_error(self):
        mgr = HookManager()
        def bad_hook(ctx):
            raise ValueError("boom")
        mgr.on(HookEvent.ERROR, callback=bad_hook, name="bad")
        results = mgr.emit(HookContext(event=HookEvent.ERROR))
        assert results[0].success is False
        assert "boom" in results[0].error

    @patch("orchestrator.hooks.subprocess.run")
    def test_emit_command(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="hello\n", stderr="")
        mgr = HookManager()
        mgr.on(HookEvent.TASK_END, command="echo hello", name="echo")
        results = mgr.emit(HookContext(event=HookEvent.TASK_END))
        assert results[0].success is True
        assert results[0].output == "hello"

    @patch("orchestrator.hooks.subprocess.run")
    def test_emit_command_fail(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        mgr = HookManager()
        mgr.on(HookEvent.TASK_END, command="false", name="fail")
        results = mgr.emit(HookContext(event=HookEvent.TASK_END))
        assert results[0].success is False

    @patch("orchestrator.hooks.subprocess.run")
    def test_emit_command_timeout(self, mock_run):
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)
        mgr = HookManager()
        mgr.on(HookEvent.TASK_END, command="sleep 999", name="slow", timeout=1)
        results = mgr.emit(HookContext(event=HookEvent.TASK_END))
        assert results[0].success is False
        assert "timed out" in results[0].error

    def test_emit_disabled_hook(self):
        mgr = HookManager()
        hook = HookConfig(event=HookEvent.SESSION_START, command="echo hi", enabled=False, name="off")
        mgr.register(hook)
        results = mgr.emit(HookContext(event=HookEvent.SESSION_START))
        assert len(results) == 0

    def test_emit_no_action(self):
        mgr = HookManager()
        hook = HookConfig(event=HookEvent.SESSION_START, name="empty")
        mgr.register(hook)
        results = mgr.emit(HookContext(event=HookEvent.SESSION_START))
        assert results[0].success is True

    def test_get_all_hooks(self):
        mgr = HookManager()
        mgr.on(HookEvent.SESSION_START, command="echo 1")
        mgr.on(HookEvent.TASK_START, command="echo 2")
        all_hooks = mgr.get_hooks()
        assert len(all_hooks) == 2

    def test_get_results(self):
        mgr = HookManager()
        called = []
        mgr.on(HookEvent.SESSION_START, callback=lambda ctx: called.append(1), name="r")
        mgr.emit(HookContext(event=HookEvent.SESSION_START))
        results = mgr.get_results(HookEvent.SESSION_START)
        assert len(results) == 1

    def test_clear_results(self):
        mgr = HookManager()
        mgr.on(HookEvent.SESSION_START, callback=lambda ctx: None, name="c")
        mgr.emit(HookContext(event=HookEvent.SESSION_START))
        mgr.clear_results()
        assert len(mgr.get_results()) == 0

    def test_load_from_config(self):
        tmpdir = tempfile.mkdtemp()
        try:
            config_path = Path(tmpdir) / "hooks.json"
            config_path.write_text(json.dumps({
                "hooks": [
                    {"event": "session_start", "command": "echo start", "name": "s"},
                    {"event": "task_end", "command": "echo done", "name": "t"},
                ]
            }))
            mgr = HookManager()
            count = mgr.load_from_config(config_path)
            assert count == 2
            assert len(mgr.get_hooks(HookEvent.SESSION_START)) == 1
        finally:
            shutil.rmtree(tmpdir)

    def test_load_from_nonexistent(self):
        mgr = HookManager()
        count = mgr.load_from_config("/nonexistent/hooks.json")
        assert count == 0

    def test_save_to_config(self):
        tmpdir = tempfile.mkdtemp()
        try:
            config_path = Path(tmpdir) / "hooks.json"
            mgr = HookManager()
            mgr.on(HookEvent.SESSION_START, command="echo hi", name="save_test")
            assert mgr.save_to_config(config_path) is True
            data = json.loads(config_path.read_text())
            assert len(data["hooks"]) == 1
            assert data["hooks"][0]["name"] == "save_test"
        finally:
            shutil.rmtree(tmpdir)

    def test_multiple_hooks_same_event(self):
        mgr = HookManager()
        results_order = []
        mgr.on(HookEvent.TASK_START, callback=lambda ctx: results_order.append(1), name="first")
        mgr.on(HookEvent.TASK_START, callback=lambda ctx: results_order.append(2), name="second")
        mgr.emit(HookContext(event=HookEvent.TASK_START))
        assert results_order == [1, 2]
