from __future__ import annotations

import secrets
from pathlib import Path


def ensure_cursor_key(state_root: Path) -> bytes:
    root = state_root / "extensions" / "octop-client"
    root.mkdir(parents=True, exist_ok=True)
    path = root / "secrets.key"
    if path.exists():
        return path.read_bytes()
    key = secrets.token_bytes(32)
    path.write_bytes(key)
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return key
