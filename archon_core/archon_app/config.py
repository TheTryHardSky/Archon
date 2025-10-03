"""Application configuration management."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from typing import Any, Dict, MutableMapping

from .utils.yaml_support import safe_load


_DEFAULTS: Dict[str, Any] = {
    "environment": "development",
    "database": {
        "path": "./archon-data.json",
    },
    "security": {
        "token_ttl": 900,
    },
    "notifications": {
        "email_enabled": False,
        "sms_enabled": False,
    },
}


@dataclass(slots=True)
class AppConfig:
    """Container for runtime configuration."""

    environment: str
    database_path: Path
    token_ttl: int
    notifications: Dict[str, bool] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, mapping: MutableMapping[str, Any]) -> "AppConfig":
        """Create a configuration object from a mapping."""
        environment = str(mapping.get("environment", _DEFAULTS["environment"]))
        database_cfg = mapping.get("database", {}) or {}
        security_cfg = mapping.get("security", {}) or {}
        notifications_cfg = mapping.get("notifications", {}) or {}

        database_path = Path(database_cfg.get("path", _DEFAULTS["database"]["path"])).expanduser()
        token_ttl = int(security_cfg.get("token_ttl", _DEFAULTS["security"]["token_ttl"]))

        notifications: Dict[str, bool] = {
            "email_enabled": bool(notifications_cfg.get("email_enabled", False)),
            "sms_enabled": bool(notifications_cfg.get("sms_enabled", False)),
        }
        return cls(
            environment=environment,
            database_path=database_path,
            token_ttl=token_ttl,
            notifications=notifications,
        )


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return safe_load(fh.read()) or {}


def load_config(config_path: str | None = None) -> AppConfig:
    """Load configuration from environment variables and optional file."""
    file_config: Dict[str, Any] = {}
    if config_path:
        cfg_path = Path(config_path)
        if cfg_path.suffix.lower() in {".yml", ".yaml"}:
            file_config = _load_yaml(cfg_path)
        else:
            file_config = _load_json(cfg_path)

    env_overrides: Dict[str, Any] = {}
    if env := os.getenv("ARCHON_ENV"):
        env_overrides["environment"] = env
    if db_path := os.getenv("ARCHON_DB_PATH"):
        env_overrides.setdefault("database", {})["path"] = db_path
    if ttl := os.getenv("ARCHON_TOKEN_TTL"):
        env_overrides.setdefault("security", {})["token_ttl"] = int(ttl)

    merged: Dict[str, Any] = {
        **_DEFAULTS,
        **file_config,
    }
    for section, values in env_overrides.items():
        if isinstance(values, MutableMapping):
            merged.setdefault(section, {}).update(values)
        else:
            merged[section] = values

    return AppConfig.from_mapping(merged)
