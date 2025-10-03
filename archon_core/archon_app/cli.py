"""Command line interface for the Archon Core application."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click

from .config import AppConfig, load_config
from .data.repository import FileTaskRepository
from .security.auth import TokenManager
from .services.task_service import TaskService
from .utils.exporter import export_tasks_to_yaml
from .utils.formatting import format_task_table
from .utils.logging import configure_logging


def _build_service(config: AppConfig) -> TaskService:
    repo = FileTaskRepository(config.database_path)
    token_manager = TokenManager(ttl_seconds=config.token_ttl)
    return TaskService(repository=repo, token_manager=token_manager)


@click.group()
@click.option(
    "--config", "config_path",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Path to a configuration file (JSON or YAML).",
)
@click.option("--verbose", is_flag=True, help="Enable verbose logging output.")
@click.pass_context
def main(ctx: click.Context, config_path: Optional[Path], verbose: bool) -> None:
    """Archon Core task orchestration toolkit."""
    configure_logging(verbose=verbose)
    config = load_config(str(config_path) if config_path else None)
    ctx.obj = {
        "config": config,
        "service": _build_service(config),
    }


@main.command("create")
@click.option("--title", prompt=True, help="Title of the task.")
@click.option("--owner", prompt=True, help="Owner responsible for the task.")
@click.option("--priority", type=click.Choice(["low", "medium", "high"], case_sensitive=False), default="medium")
@click.option("--description", default="", help="Optional task description.")
@click.pass_context
def create_task(ctx: click.Context, title: str, owner: str, priority: str, description: str) -> None:
    """Create a new task."""
    service: TaskService = ctx.obj["service"]
    task = service.create_task(title=title, owner=owner, priority=priority, description=description)
    click.echo(f"Task created with id {task.identifier}")


@main.command("list")
@click.pass_context
def list_tasks(ctx: click.Context) -> None:
    """List all tasks."""
    service: TaskService = ctx.obj["service"]
    tasks = service.list_tasks()
    click.echo(format_task_table(tasks))


@main.command("complete")
@click.argument("task_id")
@click.pass_context
def complete_task(ctx: click.Context, task_id: str) -> None:
    """Mark a task as completed."""
    service: TaskService = ctx.obj["service"]
    token = service.complete_task(task_id)
    click.echo(json.dumps({"task_id": task_id, "completion_token": token}))


@main.command("export")
@click.argument("output", type=click.Path(dir_okay=False, path_type=Path))
@click.pass_context
def export_tasks(ctx: click.Context, output: Path) -> None:
    """Export all tasks to a YAML file."""
    service: TaskService = ctx.obj["service"]
    tasks = service.list_tasks()
    export_tasks_to_yaml(tasks, output)
    click.echo(f"Exported {len(tasks)} tasks to {output}")


@main.command("purge")
@click.option("--force", is_flag=True, help="Confirm deletion of all tasks.")
@click.pass_context
def purge_tasks(ctx: click.Context, force: bool) -> None:
    """Purge all tasks from the repository."""
    if not force:
        raise click.UsageError("Refusing to purge without --force")
    service: TaskService = ctx.obj["service"]
    count = service.purge_tasks()
    click.echo(f"Purged {count} tasks")
