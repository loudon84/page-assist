from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from uuid import uuid4

from page_assist_octop_client.config import load_config
from page_assist_octop_client.host.fixture import FixtureHostPort
from page_assist_octop_client.integration.register import register, reset_registry
from page_assist_octop_client.storage.db import Store
from page_assist_octop_client.timeutil import rfc3339


def _print(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _base(command: str, status: str, code: str, **extra) -> dict:
    payload = {
        "operation_id": str(uuid4()),
        "command": command,
        "status": status,
        "code": code,
        "release_id": extra.pop("release_id", None),
        "previous_release_id": extra.pop("previous_release_id", None),
        "stage": extra.pop("stage", "none"),
        "changed": extra.pop("changed", False),
        "checks": extra.pop("checks", []),
        "receipt_path": extra.pop("receipt_path", None),
    }
    payload.update(extra)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="page_assist_octop_client")
    parser.add_argument("command", choices=["doctor", "status", "migrate", "verify"])
    parser.add_argument("--config", default=None)
    parser.add_argument("--state-root", default=None)
    args = parser.parse_args(argv)
    try:
        state_root = Path(args.state_root or "./octop-state")
        if args.command == "doctor":
            checks = [
                {"name": "python", "ok": sys.version_info >= (3, 12)},
                {"name": "state_root_writable", "ok": _writable(state_root)},
            ]
            ok = all(c["ok"] for c in checks)
            _print(_base("doctor", "ok" if ok else "blocked", "OK" if ok else "PRECHECK_FAILED", checks=checks, stage="precheck"))
            return 0 if ok else 3
        if args.command == "migrate":
            db = Store(state_root / "octop-business.sqlite")
            result = db.migrate()
            db.close()
            _print(_base("migrate", "ok", "OK", stage="migrate", changed=bool(result["applied"]), checks=[result]))
            return 0
        if args.command == "status":
            db_path = state_root / "octop-business.sqlite"
            ready = db_path.exists()
            _print(_base("status", "ok" if ready else "missing", "OK" if ready else "NOT_INSTALLED", stage="status", changed=False))
            return 0
        if args.command == "verify":
            reset_registry()
            host = FixtureHostPort(state_root)
            cfg = {
                "schema_version": 1,
                "enabled": True,
                "public_origin": "https://octop.example.internal",
                "allowed_clients": [
                    {
                        "client_id": "page-assist-chrome",
                        "extension_origin": "chrome-extension://abcdefghijklmnopqrstuvwxyz123456",
                        "redirect_uri": "https://abcdefghijklmnopqrstuvwxyz123456.chromiumapp.org/",
                    }
                ],
                "state_root": str(state_root),
                "host_api_version": 1,
                "worker_count": 1,
                "session_ttl_seconds": 28800,
                "log_level": "INFO",
                "fixture_mode": True,
            }
            if args.config:
                cfg = load_config(args.config, state_root=state_root).__dict__  # type: ignore[assignment]
            module = register(_noop_app, host, cfg if not args.config else load_config(args.config, state_root=state_root))
            ok = module.state == "READY"
            _print(_base("verify", "ok" if ok else "failed", "OK" if ok else "VERIFY_FAILED", stage="verify", checks=[{"state": module.state}]))
            return 0 if ok else 3
        _print(_base(args.command, "error", "CONFIG_INVALID", stage="precheck"))
        return 2
    except Exception as exc:
        _print(_base(args.command, "error", "FAILED", stage="failed", checks=[{"error": type(exc).__name__}]))
        return 3


async def _noop_app(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": [(b"content-type", b"application/json")]})
    await send({"type": "http.response.body", "body": b'{"ok":true}'})


def _writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / f".probe-{uuid4().hex}"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
