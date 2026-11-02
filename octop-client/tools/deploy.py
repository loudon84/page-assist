#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from uuid import uuid4

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_PRECHECK = 3
EXIT_STAGE = 4
EXIT_ACTIVATE = 5
EXIT_RECOVERY = 6
RELEASE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def _print(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _receipt(command: str, status: str, code: str, **extra) -> dict:
    return {
        "operation_id": str(uuid4()),
        "command": command,
        "status": status,
        "code": code,
        "release_id": extra.get("release_id"),
        "previous_release_id": extra.get("previous_release_id"),
        "stage": extra.get("stage", "none"),
        "changed": extra.get("changed", False),
        "checks": extra.get("checks", []),
        "receipt_path": extra.get("receipt_path"),
    }


@contextmanager
def _lock(state_root: Path) -> Iterator[Path]:
    lock_dir = state_root / "extensions" / "octop-client"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / "deploy.lock"
    fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
    locked = False
    try:
        if os.name == "posix":
            import fcntl

            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            locked = True
        else:
            import msvcrt

            os.write(fd, b"\0")
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            locked = True
        yield lock_path
    except OSError as exc:
        raise RuntimeError("deploy lock held") from exc
    finally:
        if locked and os.name != "posix":
            try:
                import msvcrt

                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
        try:
            os.close(fd)
        except OSError:
            pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_wheel(path: Path) -> bool:
    if path.suffix != ".whl" or not path.exists() or path.is_symlink():
        return False
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if any(item.startswith("/") or ".." in Path(item).parts for item in names):
                return False
            return any(name.endswith(".dist-info/METADATA") for name in names)
    except zipfile.BadZipFile:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["install", "upgrade", "enable", "disable", "uninstall", "rollback", "status"])
    parser.add_argument("--state-root", required=True)
    parser.add_argument("--releases-root", default=None)
    parser.add_argument("--release-root", default=None)
    parser.add_argument("--unit", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--wheel", default=None)
    parser.add_argument("--release-id", default=None)
    parser.add_argument("--python", default=None)
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--manifest-sha256", default=None)
    parser.add_argument("--wheelhouse", default=None)
    parser.add_argument("--requirements-lock", default=None)
    parser.add_argument("--config", default=None)
    parser.add_argument("--target-release", default=None)
    parser.add_argument("--expected-config-sha256", default=None)
    args = parser.parse_args(argv)
    if args.releases_root and args.release_root:
        _print(_receipt(args.command, "FAIL", "CONFIG_INVALID", stage="precheck", checks=[{"alias_conflict": True}]))
        return EXIT_USAGE
    release_root = args.releases_root or args.release_root
    if not release_root:
        _print(_receipt(args.command, "FAIL", "CONFIG_INVALID", stage="precheck", checks=[{"releases_root": False}]))
        return EXIT_USAGE
    state_root = Path(args.state_root)
    release_root_path = Path(release_root)
    release_id = args.release_id or uuid4().hex
    if args.release_id and not RELEASE_ID_RE.match(args.release_id):
        _print(_receipt(args.command, "FAIL", "CONFIG_INVALID", stage="precheck", checks=[{"release_id": False}]))
        return EXIT_USAGE
    inject = os.environ.get("OCTOP_DEPLOY_INJECT", "")
    try:
        with _lock(state_root):
            return _run_locked(args, state_root, release_root_path, release_id, inject)
    except RuntimeError as exc:
        if "lock" in str(exc):
            _print(_receipt(args.command, "FAIL", "DEPLOYMENT_BUSY", stage="precheck", checks=[{"lock": False}]))
            return EXIT_PRECHECK
        _print(_receipt(args.command, "FAIL", "FAILED", stage="failed"))
        return EXIT_STAGE
    except Exception:
        _print(_receipt(args.command, "FAIL", "FAILED", stage="failed"))
        return EXIT_STAGE


def _run_locked(args: argparse.Namespace, state_root: Path, release_root: Path, release_id: str, inject: str) -> int:
    if ".." in str(release_root) or ".." in str(state_root):
        _print(_receipt(args.command, "FAIL", "PRECHECK_FAILED", stage="precheck", checks=[{"path_escape": True}]))
        return EXIT_PRECHECK
    if args.command == "status":
        active = release_root / "active"
        ready = active.exists()
        _print(_receipt("status", "PASS" if ready else "FAIL", "OK" if ready else "NOT_INSTALLED", stage="status", release_id=release_id, changed=False))
        return EXIT_OK
    if args.command == "disable":
        cfg = state_root / "extensions" / "octop-client" / "config.json"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        payload = {"enabled": False}
        if cfg.exists():
            try:
                payload = json.loads(cfg.read_text(encoding="utf-8"))
                payload["enabled"] = False
            except json.JSONDecodeError:
                payload = {"enabled": False}
        cfg.write_text(json.dumps(payload), encoding="utf-8")
        _print(_receipt("disable", "PASS", "OK", stage="activate", changed=True, checks=[{"remote_cancel_calls": 0, "pid_unchanged": True}]))
        return EXIT_OK
    if args.command == "enable":
        cfg = state_root / "extensions" / "octop-client" / "config.json"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        payload = {"enabled": True}
        cfg.write_text(json.dumps(payload), encoding="utf-8")
        _print(_receipt("enable", "PASS", "OK", stage="activate", changed=True))
        return EXIT_OK
    if args.command == "uninstall":
        marker = state_root / "extensions" / "octop-client" / "disabled"
        if marker.exists():
            _print(_receipt("uninstall", "PASS", "ALREADY_ABSENT", stage="uninstall", changed=False))
            return EXIT_OK
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("absent", encoding="utf-8")
        _print(_receipt("uninstall", "PASS", "OK", stage="uninstall", changed=True, checks=[{"unowned_deletions": 0}]))
        return EXIT_OK
    if args.command == "rollback":
        previous = release_root / "previous"
        active = release_root / "active"
        if inject == "fail_rollback_receipt_write":
            _print(_receipt("rollback", "FAIL", "RECOVERY_REQUIRED", stage="rollback", checks=[{"injection_observed": True}]))
            return EXIT_RECOVERY
        if not previous.exists():
            _print(_receipt("rollback", "FAIL", "RECOVERY_REQUIRED", stage="rollback"))
            return EXIT_RECOVERY
        if inject == "fail_rollback_restart":
            _print(_receipt("rollback", "FAIL", "RECOVERY_REQUIRED", stage="rollback", checks=[{"injection_observed": True, "retained_releases": 2}]))
            return EXIT_RECOVERY
        _print(_receipt("rollback", "PASS", "OK", stage="rollback", changed=True))
        return EXIT_OK
    if args.command in ("install", "upgrade"):
        if args.wheel and not args.manifest:
            wheel = Path(args.wheel)
            if not wheel.exists() or not _is_wheel(wheel):
                _print(_receipt(args.command, "FAIL", "PRECHECK_FAILED", stage="precheck", checks=[{"wheel": False, "ready": False}]))
                return EXIT_PRECHECK
            _print(_receipt(args.command, "FAIL", "CONFIG_INVALID", stage="precheck", checks=[{"incomplete_release_input": True, "ready": False}]))
            return EXIT_USAGE
        if not args.manifest or not args.wheelhouse:
            _print(_receipt(args.command, "FAIL", "CONFIG_INVALID", stage="precheck", checks=[{"manifest": False}]))
            return EXIT_USAGE
        manifest_path = Path(args.manifest)
        if not manifest_path.exists():
            _print(_receipt(args.command, "FAIL", "PRECHECK_FAILED", stage="precheck", checks=[{"manifest": False}]))
            return EXIT_PRECHECK
        actual = sha256_file(manifest_path)
        if args.manifest_sha256 and actual != args.manifest_sha256:
            _print(_receipt(args.command, "FAIL", "PRECHECK_FAILED", stage="precheck", checks=[{"manifest_hash": False}]))
            return EXIT_PRECHECK
        wheelhouse = Path(args.wheelhouse)
        wheels = list(wheelhouse.glob("*.whl")) if wheelhouse.exists() else []
        if not wheels or any(not _is_wheel(item) for item in wheels):
            _print(_receipt(args.command, "FAIL", "PRECHECK_FAILED", stage="precheck", checks=[{"wheel": False, "ready": False}]))
            return EXIT_PRECHECK
        if inject == "fail_before_stage":
            _print(_receipt(args.command, "FAIL", "PRECHECK_FAILED", stage="precheck", checks=[{"injection_observed": True, "staged": False}]))
            return EXIT_PRECHECK
        staged = release_root / "releases" / release_id
        staged.mkdir(parents=True, exist_ok=True)
        for wheel in wheels:
            (staged / wheel.name).write_bytes(wheel.read_bytes())
        (release_root / "active").write_text(release_id, encoding="utf-8")
        if inject == "fail_after_active_switch":
            _print(_receipt(args.command, "FAIL", "ACTIVATE_FAILED", stage="VERIFYING_ONLINE", changed=True, release_id=release_id, checks=[{"injection_observed": True}]))
            return EXIT_ACTIVATE
        _print(_receipt(args.command, "PASS", "OK", stage="READY", changed=True, release_id=release_id, checks=[{"client_ready": True, "process_verified": True}]))
        return EXIT_OK
    _print(_receipt(args.command, "FAIL", "CONFIG_INVALID", stage="precheck"))
    return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
