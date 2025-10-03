"""Data models used by the Archon Core application."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import secrets
from typing import Iterable, List

_PRIORITY_LEVELS = {"low", "medium", "high"}


def _validate_priority(priority: str) -> str:
    normalized = priority.lower()
    if normalized not in _PRIORITY_LEVELS:
        raise ValueError(f"Unsupported priority level: {priority!r}")
    return normalized


def _default_identifier() -> str:
    return secrets.token_urlsafe(12)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Task:
    """Representation of a task managed by the orchestrator."""

    title: str
    owner: str
    priority: str
    description: str = ""
    identifier: str = field(default_factory=_default_identifier)
    created_at: datetime = field(default_factory=_utcnow)
    completed_at: datetime | None = None
    completion_token: str | None = None

    def __post_init__(self) -> None:
        self.priority = _validate_priority(self.priority)

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "identifier": self.identifier,
            "title": self.title,
            "owner": self.owner,
            "priority": self.priority,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "completion_token": self.completion_token,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, str | None]) -> "Task":
        created_at = datetime.fromisoformat(str(payload["created_at"])) if payload.get("created_at") else _utcnow()
        completed_at = (
            datetime.fromisoformat(str(payload["completed_at"]))
            if payload.get("completed_at")
            else None
        )
        return cls(
            identifier=str(payload.get("identifier", _default_identifier())),
            title=str(payload.get("title", "Untitled")),
            owner=str(payload.get("owner", "Unknown")),
            priority=str(payload.get("priority", "medium")),
            description=str(payload.get("description", "")),
            created_at=created_at,
            completed_at=completed_at,
            completion_token=str(payload.get("completion_token")) if payload.get("completion_token") else None,
        )


def serialize_tasks(tasks: Iterable[Task]) -> List[dict[str, str | None]]:
    return [task.to_dict() for task in tasks]


def deserialize_tasks(records: Iterable[dict[str, str | None]]) -> List[Task]:
    return [Task.from_dict(record) for record in records]
