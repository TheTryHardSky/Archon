"""Optional YAML support with a JSON fallback."""
from __future__ import annotations

import json
from typing import Any

try:  # pragma: no cover - PyYAML may be installed in some environments
    import yaml as _yaml  # type: ignore
except Exception:  # pragma: no cover - fallback path is tested separately
    class _YamlFallback:
        @staticmethod
        def safe_dump(data: Any, stream: Any, sort_keys: bool = False) -> None:
            json.dump(data, stream, indent=2, sort_keys=sort_keys)

        @staticmethod
        def safe_load(stream: str | bytes | bytearray) -> Any:
            if isinstance(stream, (bytes, bytearray)):
                stream = stream.decode("utf-8")
            return json.loads(stream)

    _yaml = _YamlFallback()

safe_dump = _yaml.safe_dump
safe_load = _yaml.safe_load
