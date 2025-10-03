"""Domain services for managing tasks."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from ..data.models import Task
from ..data.repository import TaskRepository
from ..security.auth import TokenManager
from ..utils.validation import ensure_non_empty


class TaskService:
    """Service for orchestrating task lifecycle events."""

    def __init__(self, repository: TaskRepository, token_manager: TokenManager):
        self._repository = repository
        self._token_manager = token_manager

    def list_tasks(self) -> List[Task]:
        return sorted(self._repository.list(), key=lambda t: t.created_at)

    def create_task(self, title: str, owner: str, priority: str, description: str = "") -> Task:
        ensure_non_empty(title=title, owner=owner)
        task = Task(title=title.strip(), owner=owner.strip(), priority=priority, description=description.strip())
        return self._repository.save(task)

    def complete_task(self, identifier: str) -> str:
        task = self._repository.get(identifier)
        if task.is_completed and task.completion_token:
            return task.completion_token
        token = self._token_manager.issue_token({"task_id": identifier})
        task.completed_at = datetime.now(timezone.utc)
        task.completion_token = token
        self._repository.save(task)
        return token

    def purge_tasks(self) -> int:
        tasks = self._repository.list()
        self._repository.replace_all([])
        return len(tasks)

    def import_tasks(self, tasks: List[Task]) -> None:
        for task in tasks:
            ensure_non_empty(title=task.title, owner=task.owner)
        self._repository.replace_all(tasks)
