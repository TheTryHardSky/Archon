from __future__ import annotations

from pathlib import Path

from archon_app.data.models import Task
from archon_app.utils.exporter import export_tasks_to_yaml
from archon_app.utils.formatting import format_task_table
from archon_app.utils.validation import ensure_non_empty
from archon_app.utils.yaml_support import safe_load


def test_export_tasks_to_yaml(tmp_path: Path) -> None:
    task = Task(title="Export", owner="QA", priority="medium")
    output = tmp_path / "tasks.yml"
    export_tasks_to_yaml([task], output)
    data = safe_load(output.read_text(encoding="utf-8"))
    assert data[0]["title"] == "Export"


def test_format_task_table_contains_headers() -> None:
    table = format_task_table([Task(title="A", owner="B", priority="low")])
    assert "Title" in table
    assert "Owner" in table


def test_ensure_non_empty_rejects_blank_values() -> None:
    try:
        ensure_non_empty(name=" ")
    except ValueError as exc:  # noqa: PERF203 - explicit exception capturing for clarity
        assert "name" in str(exc)
    else:  # pragma: no cover - defensive guard
        raise AssertionError("Expected ValueError")
