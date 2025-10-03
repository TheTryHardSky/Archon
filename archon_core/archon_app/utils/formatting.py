"""Helpers for formatting output tables."""
from __future__ import annotations

from typing import Iterable

from ..data.models import Task


def format_task_table(tasks: Iterable[Task]) -> str:
    headers = ["ID", "Title", "Owner", "Priority", "Completed"]
    rows = []
    for task in tasks:
        rows.append([
            task.identifier,
            task.title,
            task.owner,
            task.priority,
            "yes" if task.is_completed else "no",
        ])
    widths = [max(len(str(col)) for col in [header] + [row[idx] for row in rows] if rows) for idx, header in enumerate(headers)]
    def format_row(row: list[str]) -> str:
        return " | ".join(col.ljust(widths[idx]) for idx, col in enumerate(row))

    lines = [format_row(headers)]
    lines.append("-+-".join("-" * width for width in widths))
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)
