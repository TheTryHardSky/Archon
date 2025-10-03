from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from archon_app.data.models import Task
from archon_app.data.repository import FileTaskRepository
from archon_app.security.auth import TokenManager
from archon_app.services.task_service import TaskService


def test_create_and_list_tasks(tmp_path: Path) -> None:
    repo = FileTaskRepository(tmp_path / "tasks.json")
    service = TaskService(repo, TokenManager(ttl_seconds=60, secret=b"secret"))
    created = service.create_task(title="Demo", owner="QA", priority="high")
    tasks = service.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].identifier == created.identifier
    assert tasks[0].priority == "high"


def test_complete_task_generates_token(tmp_path: Path) -> None:
    repo = FileTaskRepository(tmp_path / "tasks.json")
    service = TaskService(repo, TokenManager(ttl_seconds=60, secret=b"secret"))
    task = service.create_task(title="Demo", owner="QA", priority="medium")
    token = service.complete_task(task.identifier)
    payload = service._token_manager.validate_token(token)
    assert payload["task_id"] == task.identifier


def test_import_tasks_replaces_existing(tmp_path: Path) -> None:
    repo = FileTaskRepository(tmp_path / "tasks.json")
    service = TaskService(repo, TokenManager(ttl_seconds=60, secret=b"secret"))
    first = Task(title="One", owner="QA", priority="low")
    second = Task(title="Two", owner="QA", priority="medium")
    service.import_tasks([first, second])
    tasks = service.list_tasks()
    assert len(tasks) == 2
    assert {t.title for t in tasks} == {"One", "Two"}


def test_complete_task_is_idempotent(tmp_path: Path) -> None:
    repo = FileTaskRepository(tmp_path / "tasks.json")
    service = TaskService(repo, TokenManager(ttl_seconds=60, secret=b"secret"))
    task = service.create_task(title="Demo", owner="QA", priority="medium")
    token1 = service.complete_task(task.identifier)
    token2 = service.complete_task(task.identifier)
    assert token1 == token2
