"""Security helpers for issuing and validating tokens."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict


class TokenManager:
    """Issue and validate signed tokens."""

    def __init__(self, ttl_seconds: int, secret: bytes | None = None):
        self._ttl = ttl_seconds
        self._secret = secret or os.urandom(32)

    def issue_token(self, payload: Dict[str, Any]) -> str:
        issued_at = datetime.now(timezone.utc)
        expiry = issued_at + timedelta(seconds=self._ttl)
        envelope = {
            "payload": payload,
            "issued_at": issued_at.isoformat(),
            "expires_at": expiry.isoformat(),
        }
        serialized = json.dumps(envelope, separators=(",", ":"), sort_keys=True).encode("utf-8")
        signature = hmac.new(self._secret, serialized, hashlib.sha256).digest()
        token_bytes = base64.urlsafe_b64encode(serialized + b"." + signature)
        return token_bytes.decode("ascii")

    def validate_token(self, token: str) -> Dict[str, Any]:
        decoded = base64.urlsafe_b64decode(token.encode("ascii"))
        serialized, signature = decoded.rsplit(b".", 1)
        expected = hmac.new(self._secret, serialized, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("Invalid token signature")
        envelope = json.loads(serialized.decode("utf-8"))
        expires_at = datetime.fromisoformat(envelope["expires_at"]).astimezone(timezone.utc)
        if datetime.now(timezone.utc) >= expires_at:
            raise ValueError("Token expired")
        return envelope["payload"]
