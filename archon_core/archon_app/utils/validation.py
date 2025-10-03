"""Validation helpers."""
from __future__ import annotations


def ensure_non_empty(**fields: str) -> None:
    for field, value in fields.items():
        if not value or not value.strip():
            raise ValueError(f"{field} must not be empty")
