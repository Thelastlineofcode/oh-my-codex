"""
Team bridge with worker management, task routing, heartbeat, and git worktree isolation.
"""
from __future__ import annotations

import json
import logging
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class WorkerStatus(Enum):
    """Status of a worker agent."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class TaskStatus(Enum):
    """Status of a team task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Worker:
    """A worker agent in the team."""
    id: str
    role: str
    status: WorkerStatus = WorkerStatus.IDLE
    current_task: str = ""
    heartbeat_at: float = 0.0
    worktree_path: str = ""


@dataclass
class TeamTask:
    """A task for the team to execute."""
    id: str
    description: str
    assigned_to: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    created_at: float = field(default_factory=time.time)
    completed_at: float = 0.0


class TeamBridge:
    """Manages team of workers with task routing and git worktree isolation."""

    def __init__(self, team_dir: str | Path | None = None) -> None:
        self._workers: dict[str, Worker] = {}
        self._tasks: dict[str, TeamTask] = {}
        self._team_dir = Path(team_dir) if team_dir else Path(".omc") / "team"
        self._team_dir.mkdir(parents=True, exist_ok=True)

    def add_worker(self, worker: Worker) -> None:
        """Add a worker to the team."""
        self._workers[worker.id] = worker

    def remove_worker(self, worker_id: str) -> bool:
        """Remove a worker from the team."""
        if worker_id in self._workers:
            del self._workers[worker_id]
            return True
        return False

    def get_worker(self, worker_id: str) -> Worker | None:
        """Get a worker by ID."""
        return self._workers.get(worker_id)

    def list_workers(self, status: WorkerStatus | None = None) -> list[Worker]:
        """List workers, optionally filtered by status."""
        if status:
            return [w for w in self._workers.values() if w.status == status]
        return list(self._workers.values())

    def add_task(self, task: TeamTask) -> None:
        """Add a task to the queue."""
        self._tasks[task.id] = task

    def claim_task(self, worker_id: str) -> TeamTask | None:
        """Atomically claim the first pending task for a worker."""
        worker = self.get_worker(worker_id)
        if not worker:
            return None

        # Find first pending task by priority (higher first), then by created_at
        pending = [t for t in self._tasks.values() if t.status == TaskStatus.PENDING]
        if not pending:
            return None

        task = sorted(pending, key=lambda t: (-t.priority, t.created_at))[0]

        # Atomic claim
        task.status = TaskStatus.IN_PROGRESS
        task.assigned_to = worker_id
        worker.status = WorkerStatus.BUSY
        worker.current_task = task.id

        return task

    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed."""
        task = self._tasks.get(task_id)
        if not task:
            return False

        task.status = TaskStatus.COMPLETED
        task.completed_at = time.time()

        # Free up the worker
        if task.assigned_to:
            worker = self.get_worker(task.assigned_to)
            if worker:
                worker.status = WorkerStatus.IDLE
                worker.current_task = ""

        return True

    def get_pending_tasks(self) -> list[TeamTask]:
        """Get all pending tasks."""
        return [t for t in self._tasks.values() if t.status == TaskStatus.PENDING]

    def heartbeat(self, worker_id: str) -> bool:
        """Update worker heartbeat timestamp."""
        worker = self.get_worker(worker_id)
        if not worker:
            return False
        worker.heartbeat_at = time.time()
        return True

    def create_worktree(self, worker_id: str, branch: str) -> str | None:
        """Create a git worktree for a worker."""
        worker = self.get_worker(worker_id)
        if not worker:
            return None

        worktree_path = str(self._team_dir / f"worktree-{worker_id}")

        try:
            result = subprocess.run(
                ["git", "worktree", "add", "-b", branch, worktree_path, "HEAD"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                worker.worktree_path = worktree_path
                return worktree_path
            logger.error(f"Failed to create worktree: {result.stderr}")
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"Error creating worktree: {e}")
            return None

    def remove_worktree(self, worker_id: str) -> bool:
        """Remove a worker's git worktree."""
        worker = self.get_worker(worker_id)
        if not worker or not worker.worktree_path:
            return False

        try:
            result = subprocess.run(
                ["git", "worktree", "remove", worker.worktree_path, "--force"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                worker.worktree_path = ""
                return True
            logger.error(f"Failed to remove worktree: {result.stderr}")
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"Error removing worktree: {e}")
            return False

    def save_state(self) -> bool:
        """Save team state to JSON file."""
        state_file = self._team_dir / "team-state.json"
        try:
            state = {
                "workers": {
                    wid: {
                        "id": w.id,
                        "role": w.role,
                        "status": w.status.value,
                        "current_task": w.current_task,
                        "heartbeat_at": w.heartbeat_at,
                        "worktree_path": w.worktree_path,
                    }
                    for wid, w in self._workers.items()
                },
                "tasks": {
                    tid: {
                        "id": t.id,
                        "description": t.description,
                        "assigned_to": t.assigned_to,
                        "status": t.status.value,
                        "priority": t.priority,
                        "created_at": t.created_at,
                        "completed_at": t.completed_at,
                    }
                    for tid, t in self._tasks.items()
                },
            }
            state_file.write_text(json.dumps(state, indent=2))
            return True
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            return False

    def load_state(self) -> bool:
        """Load team state from JSON file."""
        state_file = self._team_dir / "team-state.json"
        if not state_file.exists():
            return False

        try:
            state = json.loads(state_file.read_text())

            # Load workers
            for wid, wdata in state.get("workers", {}).items():
                worker = Worker(
                    id=wdata["id"],
                    role=wdata["role"],
                    status=WorkerStatus(wdata["status"]),
                    current_task=wdata["current_task"],
                    heartbeat_at=wdata["heartbeat_at"],
                    worktree_path=wdata["worktree_path"],
                )
                self._workers[wid] = worker

            # Load tasks
            for tid, tdata in state.get("tasks", {}).items():
                task = TeamTask(
                    id=tdata["id"],
                    description=tdata["description"],
                    assigned_to=tdata["assigned_to"],
                    status=TaskStatus(tdata["status"]),
                    priority=tdata["priority"],
                    created_at=tdata["created_at"],
                    completed_at=tdata["completed_at"],
                )
                self._tasks[tid] = task

            return True
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return False
