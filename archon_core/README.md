# Archon Core

Archon Core is a demonstration-quality task orchestration toolkit. The project showcases
secure coding practices, modular architecture, and comprehensive testing in a Python
package suitable for internal quality assurance exercises.

## Features

- Configuration management with environment-aware overrides
- Cryptographically strong token generation and signature validation
- Task orchestration service with pluggable persistence and notification pipelines
- CLI for managing tasks and monitoring orchestrator health
- YAML export/import utilities for structured backups

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
archon-core --help
```

## Testing

```bash
pip install -e .[dev]
pytest
```
