"""Task repository implementations."""
from __future__ import annotations

from pathlib import Path
from threading import RLock
from typing import Iterable, List
import json

from .models import Task, deserialize_tasks, serialize_tasks


class TaskRepository:
    """Abstract repository interface."""

    def list(self) -> List[Task]:
        raise NotImplementedError

    def save(self, task: Task) -> Task:
        raise NotImplementedError

    def get(self, identifier: str) -> Task:
        raise NotImplementedError

    def delete(self, identifier: str) -> None:
        raise NotImplementedError

    def replace_all(self, tasks: Iterable[Task]) -> None:
        raise NotImplementedError


class FileTaskRepository(TaskRepository):
    """File-backed task repository with thread-safe access."""

    def __init__(self, path: Path):
        self._path = path
        self._lock = RLock()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("[]", encoding="utf-8")

    def _read(self) -> List[Task]:
        with self._lock:
            raw = self._path.read_text(encoding="utf-8")
            data = json.loads(raw or "[]")
            return deserialize_tasks(data)

    def _write(self, tasks: Iterable[Task]) -> None:
        with self._lock:
            payload = json.dumps(serialize_tasks(tasks), indent=2)
            self._path.write_text(payload, encoding="utf-8")

    def list(self) -> List[Task]:
        return self._read()

    def save(self, task: Task) -> Task:
        tasks = self._read()
        tasks = [t for t in tasks if t.identifier != task.identifier]
        tasks.append(task)
        self._write(tasks)
        return task

    def get(self, identifier: str) -> Task:
        for task in self._read():
            if task.identifier == identifier:
                return task
        raise KeyError(f"Task {identifier!r} not found")

    def delete(self, identifier: str) -> None:
        tasks = [t for t in self._read() if t.identifier != identifier]
        self._write(tasks)

    def replace_all(self, tasks: Iterable[Task]) -> None:
        self._write(list(tasks))

    def purge(self) -> int:
        with self._lock:
            self._path.write_text("[]", encoding="utf-8")
        return 0
