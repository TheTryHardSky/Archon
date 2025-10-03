"""Utilities to export tasks to YAML."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ..data.models import Task, serialize_tasks
from .yaml_support import safe_dump


def export_tasks_to_yaml(tasks: Iterable[Task], output: Path) -> None:
    payload = serialize_tasks(tasks)
    with output.open("w", encoding="utf-8") as fh:
        safe_dump(payload, fh, sort_keys=False)
