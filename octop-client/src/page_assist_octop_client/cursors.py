from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any

from page_assist_octop_client.jcs import canonical_json


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _sign(key: bytes, payload: bytes) -> str:
    return _b64(hmac.new(key, payload, hashlib.sha256).digest()[:24])


def issue_cursor(key: bytes, claims: dict[str, Any]) -> str:
    body = canonical_json(claims).encode("utf-8")
    return _b64(body) + "." + _sign(key, body)


def read_cursor(key: bytes, token: str) -> dict[str, Any] | None:
    if "." not in token:
        return None
    body_b64, sig = token.rsplit(".", 1)
    try:
        body = base64.urlsafe_b64decode(body_b64 + "=" * (-len(body_b64) % 4))
    except Exception:
        return None
    if not hmac.compare_digest(_sign(key, body), sig):
        return None
    try:
        claims = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(claims, dict):
        return None
    return claims
