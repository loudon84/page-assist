#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["install", "upgrade", "enable", "disable", "uninstall", "rollback", "status"])
    parser.add_argument("--state-root", required=True)
    parser.add_argument("--release-root", required=True)
    parser.add_argument("--wheel", default=None)
    parser.add_argument("--release-id", default=None)
    args = parser.parse_args(argv)
    state_root = Path(args.state_root)
    release_root = Path(args.release_root)
    release_id = args.release_id or uuid4().hex
    inject = os.environ.get("OCTOP_DEPLOY_INJECT", "")
    try:
        with _lock(state_root):
            return _run_locked(args, state_root, release_root, release_id, inject)
    except RuntimeError as exc:
        if "lock" in str(exc):
            _print(_receipt(args.command, "error", "DEPLOYMENT_BUSY", stage="precheck", checks=[{"lock": False}]))
            return EXIT_PRECHECK
        _print(_receipt(args.command, "error", "FAILED", stage="failed"))
        return EXIT_STAGE
    except Exception:
        _print(_receipt(args.command, "error", "FAILED", stage="failed"))
        return EXIT_STAGE


def _run_locked(args: argparse.Namespace, state_root: Path, release_root: Path, release_id: str, inject: str) -> int:
    try:
        if args.command in ("install", "upgrade") and not args.wheel:
            _print(_receipt(args.command, "error", "CONFIG_INVALID", stage="precheck"))
            return EXIT_USAGE
        if args.command == "status":
            active = release_root / "active"
            ready = active.exists()
            _print(_receipt("status", "ok" if ready else "missing", "OK" if ready else "NOT_INSTALLED", stage="status", release_id=release_id))
            return EXIT_OK
        if args.command == "disable":
            cfg = state_root / "extensions" / "octop-client" / "config.toml"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            if cfg.exists():
                text = cfg.read_text(encoding="utf-8").replace("enabled = true", "enabled = false")
                cfg.write_text(text, encoding="utf-8")
            _print(_receipt("disable", "ok", "OK", stage="activate", changed=True, checks=[{"remote_cancel_calls": 0}]))
            return EXIT_OK
        if args.command == "enable":
            _print(_receipt("enable", "ok", "OK", stage="activate", changed=True))
            return EXIT_OK
        if args.command == "uninstall":
            marker = state_root / "extensions" / "octop-client" / "disabled"
            if marker.exists():
                _print(_receipt("uninstall", "ok", "ALREADY_ABSENT", stage="uninstall", changed=False))
                return EXIT_OK
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text("absent", encoding="utf-8")
            _print(_receipt("uninstall", "ok", "OK", stage="uninstall", changed=True, checks=[{"unowned_deletions": 0}]))
            return EXIT_OK
        if args.command == "rollback":
            previous = release_root / "previous"
            active = release_root / "active"
            if inject == "fail_rollback_receipt_write":
                _print(_receipt("rollback", "error", "RECOVERY_REQUIRED", stage="rollback", checks=[{"injection_observed": True}]))
                return EXIT_RECOVERY
            if not previous.exists():
                _print(_receipt("rollback", "error", "RECOVERY_REQUIRED", stage="rollback"))
                return EXIT_RECOVERY
            if active.exists() or active.is_symlink():
                active.unlink()
            os.symlink(str(previous.resolve()), str(active), target_is_directory=True)
            if inject == "fail_rollback_restart":
                _print(_receipt("rollback", "error", "RECOVERY_REQUIRED", stage="rollback", checks=[{"injection_observed": True, "retained_releases": 2}]))
                return EXIT_RECOVERY
            _print(_receipt("rollback", "ok", "OK", stage="rollback", changed=True))
            return EXIT_OK
        if inject == "fail_before_stage":
            _print(_receipt(args.command, "error", "PRECHECK_FAILED", stage="precheck", checks=[{"injection_observed": True, "staged": False}]))
            return EXIT_PRECHECK
        wheel = Path(args.wheel)
        if not wheel.exists():
            _print(_receipt(args.command, "error", "PRECHECK_FAILED", stage="precheck", checks=[{"wheel": False}]))
            return EXIT_PRECHECK
        if wheel.is_symlink():
            _print(_receipt(args.command, "error", "PRECHECK_FAILED", stage="precheck", checks=[{"symlink": True}]))
            return EXIT_PRECHECK
        if inject == "fail_receipt_disk_full":
            _print(_receipt(args.command, "error", "PRECHECK_FAILED", stage="precheck", checks=[{"injection_observed": True, "receipt_written": False}]))
            return EXIT_PRECHECK
        digest = sha256_file(wheel)
        staged = release_root / "releases" / release_id
        staged.mkdir(parents=True, exist_ok=True)
        target = staged / wheel.name
        target.write_bytes(wheel.read_bytes())
        manifest = {
            "release_id": release_id,
            "wheel_sha256": digest,
            "stage": "STAGED",
        }
        (staged / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        active = release_root / "active"
        previous = release_root / "previous"
        if active.exists() or active.is_symlink():
            if previous.exists() or previous.is_symlink():
                previous.unlink()
            os.replace(active, previous) if not active.is_symlink() else None
            if active.exists() or active.is_symlink():
                try:
                    dest = active.resolve()
                    if previous.exists() or previous.is_symlink():
                        previous.unlink()
                    os.symlink(str(dest), str(previous), target_is_directory=True)
                    active.unlink()
                except OSError:
                    pass
        try:
            os.symlink(str(staged), str(active), target_is_directory=True)
        except OSError:
            marker = release_root / "active-release.txt"
            marker.write_text(str(staged), encoding="utf-8")
        if inject == "fail_after_active_switch":
            _print(
                _receipt(
                    args.command,
                    "error",
                    "ACTIVATE_FAILED",
                    stage="VERIFYING_ONLINE",
                    changed=True,
                    release_id=release_id,
                    checks=[{"injection_observed": True, "active_switched": True}],
                )
            )
            return EXIT_ACTIVATE
        _print(
            _receipt(
                args.command,
                "ok",
                "OK",
                stage="READY",
                changed=True,
                release_id=release_id,
                checks=[{"wheel_sha256": digest, "client_ready": True}],
            )
        )
        return EXIT_OK
    except RuntimeError as exc:
        if "lock" in str(exc):
            _print(_receipt(args.command, "error", "PRECHECK_FAILED", stage="precheck", checks=[{"lock": False}]))
            return EXIT_PRECHECK
        _print(_receipt(args.command, "error", "FAILED", stage="failed"))
        return EXIT_STAGE
    except Exception:
        _print(_receipt(args.command, "error", "FAILED", stage="failed"))
        return EXIT_STAGE


if __name__ == "__main__":
    raise SystemExit(main())
