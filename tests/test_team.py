"""Tests for team module."""

import pytest
import json
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from orchestrator.team import (
    WorkerStatus,
    TaskStatus,
    Worker,
    TeamTask,
    TeamBridge,
)


class TestWorkerStatus:
    def test_worker_status_values(self):
        assert WorkerStatus.IDLE.value == "idle"
        assert WorkerStatus.BUSY.value == "busy"
        assert WorkerStatus.ERROR.value == "error"
        assert WorkerStatus.OFFLINE.value == "offline"


class TestTaskStatus:
    def test_task_status_values(self):
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"


class TestWorker:
    def test_worker_creation(self):
        worker = Worker(id="w1", role="executor")
        assert worker.id == "w1"
        assert worker.role == "executor"
        assert worker.status == WorkerStatus.IDLE
        assert worker.current_task == ""
        assert worker.heartbeat_at == 0.0
        assert worker.worktree_path == ""

    def test_worker_with_status(self):
        worker = Worker(id="w2", role="architect", status=WorkerStatus.BUSY)
        assert worker.status == WorkerStatus.BUSY


class TestTeamTask:
    def test_task_creation(self):
        task = TeamTask(id="t1", description="Fix bug")
        assert task.id == "t1"
        assert task.description == "Fix bug"
        assert task.assigned_to == ""
        assert task.status == TaskStatus.PENDING
        assert task.priority == 0
        assert task.created_at > 0
        assert task.completed_at == 0.0

    def test_task_with_priority(self):
        task = TeamTask(id="t2", description="Urgent", priority=10)
        assert task.priority == 10


class TestTeamBridge:
    def test_init_default_dir(self):
        bridge = TeamBridge()
        assert bridge._team_dir == Path(".omc") / "team"

    def test_init_custom_dir(self):
        tmpdir = tempfile.mkdtemp()
        try:
            bridge = TeamBridge(team_dir=tmpdir)
            assert bridge._team_dir == Path(tmpdir)
        finally:
            shutil.rmtree(tmpdir)

    def test_add_worker(self):
        bridge = TeamBridge()
        worker = Worker(id="w1", role="executor")
        bridge.add_worker(worker)
        assert bridge.get_worker("w1") == worker

    def test_remove_worker(self):
        bridge = TeamBridge()
        worker = Worker(id="w1", role="executor")
        bridge.add_worker(worker)
        assert bridge.remove_worker("w1") is True
        assert bridge.get_worker("w1") is None

    def test_remove_nonexistent_worker(self):
        bridge = TeamBridge()
        assert bridge.remove_worker("nope") is False

    def test_get_worker(self):
        bridge = TeamBridge()
        worker = Worker(id="w1", role="executor")
        bridge.add_worker(worker)
        retrieved = bridge.get_worker("w1")
        assert retrieved is not None
        assert retrieved.id == "w1"

    def test_get_nonexistent_worker(self):
        bridge = TeamBridge()
        assert bridge.get_worker("nope") is None

    def test_list_workers_all(self):
        bridge = TeamBridge()
        w1 = Worker(id="w1", role="executor", status=WorkerStatus.IDLE)
        w2 = Worker(id="w2", role="architect", status=WorkerStatus.BUSY)
        bridge.add_worker(w1)
        bridge.add_worker(w2)
        workers = bridge.list_workers()
        assert len(workers) == 2

    def test_list_workers_by_status(self):
        bridge = TeamBridge()
        w1 = Worker(id="w1", role="executor", status=WorkerStatus.IDLE)
        w2 = Worker(id="w2", role="architect", status=WorkerStatus.BUSY)
        bridge.add_worker(w1)
        bridge.add_worker(w2)
        idle = bridge.list_workers(status=WorkerStatus.IDLE)
        assert len(idle) == 1
        assert idle[0].id == "w1"

    def test_add_task(self):
        bridge = TeamBridge()
        task = TeamTask(id="t1", description="Fix bug")
        bridge.add_task(task)
        pending = bridge.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0].id == "t1"

    def test_claim_task_atomic(self):
        bridge = TeamBridge()
        worker = Worker(id="w1", role="executor")
        bridge.add_worker(worker)
        task = TeamTask(id="t1", description="Fix bug")
        bridge.add_task(task)

        claimed = bridge.claim_task("w1")
        assert claimed is not None
        assert claimed.id == "t1"
        assert claimed.status == TaskStatus.IN_PROGRESS
        assert claimed.assigned_to == "w1"
        assert worker.status == WorkerStatus.BUSY
        assert worker.current_task == "t1"

    def test_claim_task_no_worker(self):
        bridge = TeamBridge()
        task = TeamTask(id="t1", description="Fix bug")
        bridge.add_task(task)
        claimed = bridge.claim_task("nope")
        assert claimed is None

    def test_claim_task_no_pending(self):
        bridge = TeamBridge()
        worker = Worker(id="w1", role="executor")
        bridge.add_worker(worker)
        claimed = bridge.claim_task("w1")
        assert claimed is None

    def test_claim_task_priority_order(self):
        bridge = TeamBridge()
        worker = Worker(id="w1", role="executor")
        bridge.add_worker(worker)

        t1 = TeamTask(id="t1", description="Low priority", priority=1)
        t2 = TeamTask(id="t2", description="High priority", priority=10)
        bridge.add_task(t1)
        time.sleep(0.01)  # Ensure different created_at
        bridge.add_task(t2)

        claimed = bridge.claim_task("w1")
        assert claimed is not None
        assert claimed.id == "t2"  # Higher priority

    def test_complete_task(self):
        bridge = TeamBridge()
        worker = Worker(id="w1", role="executor")
        bridge.add_worker(worker)
        task = TeamTask(id="t1", description="Fix bug")
        bridge.add_task(task)

        bridge.claim_task("w1")
        assert bridge.complete_task("t1") is True

        completed_task = bridge._tasks["t1"]
        assert completed_task.status == TaskStatus.COMPLETED
        assert completed_task.completed_at > 0
        assert worker.status == WorkerStatus.IDLE
        assert worker.current_task == ""

    def test_complete_nonexistent_task(self):
        bridge = TeamBridge()
        assert bridge.complete_task("nope") is False

    def test_get_pending_tasks(self):
        bridge = TeamBridge()
        t1 = TeamTask(id="t1", description="Pending")
        t2 = TeamTask(id="t2", description="In progress", status=TaskStatus.IN_PROGRESS)
        bridge.add_task(t1)
        bridge.add_task(t2)

        pending = bridge.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0].id == "t1"

    def test_heartbeat(self):
        bridge = TeamBridge()
        worker = Worker(id="w1", role="executor")
        bridge.add_worker(worker)

        before = worker.heartbeat_at
        time.sleep(0.01)
        assert bridge.heartbeat("w1") is True
        assert worker.heartbeat_at > before

    def test_heartbeat_nonexistent_worker(self):
        bridge = TeamBridge()
        assert bridge.heartbeat("nope") is False

    @patch("orchestrator.team.subprocess.run")
    def test_create_worktree(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        tmpdir = tempfile.mkdtemp()
        try:
            bridge = TeamBridge(team_dir=tmpdir)
            worker = Worker(id="w1", role="executor")
            bridge.add_worker(worker)

            path = bridge.create_worktree("w1", "feature-branch")
            assert path is not None
            assert path == str(Path(tmpdir) / "worktree-w1")
            assert worker.worktree_path == path

            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args[0] == "git"
            assert args[1] == "worktree"
            assert args[2] == "add"
        finally:
            shutil.rmtree(tmpdir)

    @patch("orchestrator.team.subprocess.run")
    def test_create_worktree_fail(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")

        tmpdir = tempfile.mkdtemp()
        try:
            bridge = TeamBridge(team_dir=tmpdir)
            worker = Worker(id="w1", role="executor")
            bridge.add_worker(worker)

            path = bridge.create_worktree("w1", "feature-branch")
            assert path is None
        finally:
            shutil.rmtree(tmpdir)

    @patch("orchestrator.team.subprocess.run")
    def test_create_worktree_no_worker(self, mock_run):
        bridge = TeamBridge()
        path = bridge.create_worktree("nope", "branch")
        assert path is None
        mock_run.assert_not_called()

    @patch("orchestrator.team.subprocess.run")
    def test_remove_worktree(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        bridge = TeamBridge()
        worker = Worker(id="w1", role="executor", worktree_path="/path/to/worktree")
        bridge.add_worker(worker)

        assert bridge.remove_worktree("w1") is True
        assert worker.worktree_path == ""

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "git"
        assert args[1] == "worktree"
        assert args[2] == "remove"

    @patch("orchestrator.team.subprocess.run")
    def test_remove_worktree_fail(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")

        bridge = TeamBridge()
        worker = Worker(id="w1", role="executor", worktree_path="/path/to/worktree")
        bridge.add_worker(worker)

        assert bridge.remove_worktree("w1") is False

    def test_remove_worktree_no_worker(self):
        bridge = TeamBridge()
        assert bridge.remove_worktree("nope") is False

    def test_remove_worktree_no_path(self):
        bridge = TeamBridge()
        worker = Worker(id="w1", role="executor")
        bridge.add_worker(worker)
        assert bridge.remove_worktree("w1") is False

    def test_save_and_load_state(self):
        tmpdir = tempfile.mkdtemp()
        try:
            bridge = TeamBridge(team_dir=tmpdir)

            # Add worker and task
            worker = Worker(id="w1", role="executor", status=WorkerStatus.BUSY, heartbeat_at=123.45)
            task = TeamTask(id="t1", description="Fix bug", priority=5, created_at=100.0)
            bridge.add_worker(worker)
            bridge.add_task(task)

            # Save
            assert bridge.save_state() is True

            # Load into new bridge
            bridge2 = TeamBridge(team_dir=tmpdir)
            assert bridge2.load_state() is True

            # Verify worker
            loaded_worker = bridge2.get_worker("w1")
            assert loaded_worker is not None
            assert loaded_worker.role == "executor"
            assert loaded_worker.status == WorkerStatus.BUSY
            assert loaded_worker.heartbeat_at == 123.45

            # Verify task
            loaded_tasks = bridge2.get_pending_tasks()
            assert len(loaded_tasks) == 1
            assert loaded_tasks[0].description == "Fix bug"
            assert loaded_tasks[0].priority == 5
        finally:
            shutil.rmtree(tmpdir)

    def test_load_state_no_file(self):
        tmpdir = tempfile.mkdtemp()
        try:
            bridge = TeamBridge(team_dir=tmpdir)
            assert bridge.load_state() is False
        finally:
            shutil.rmtree(tmpdir)

    def test_save_state_complex(self):
        tmpdir = tempfile.mkdtemp()
        try:
            bridge = TeamBridge(team_dir=tmpdir)

            # Add multiple workers and tasks
            w1 = Worker(id="w1", role="executor")
            w2 = Worker(id="w2", role="architect", status=WorkerStatus.ERROR)
            t1 = TeamTask(id="t1", description="Task 1")
            t2 = TeamTask(id="t2", description="Task 2", status=TaskStatus.COMPLETED, completed_at=200.0)

            bridge.add_worker(w1)
            bridge.add_worker(w2)
            bridge.add_task(t1)
            bridge.add_task(t2)

            assert bridge.save_state() is True

            state_file = Path(tmpdir) / "team-state.json"
            assert state_file.exists()

            data = json.loads(state_file.read_text())
            assert len(data["workers"]) == 2
            assert len(data["tasks"]) == 2
            assert data["workers"]["w2"]["status"] == "error"
            assert data["tasks"]["t2"]["status"] == "completed"
        finally:
            shutil.rmtree(tmpdir)
