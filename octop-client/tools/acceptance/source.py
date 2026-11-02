"""Collect actual git identity. Never impersonate a baseline SHA."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

PA_BASELINE = "ff1df1ce4df8b3d12be231fb40857fd3a46fc88c"
OC_BASELINE = "e3041c452ffc870f754378bd99d964349580d3f9"


def _run(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _dirty_manifest(repo: Path) -> tuple[bool, str | None]:
    porcelain = _run(repo, "status", "--porcelain")
    if not porcelain:
        return False, None
    digest = hashlib.sha256(porcelain.encode("utf-8")).hexdigest()
    return True, digest


def collect_source(page_assist_root: Path, octop_root: Path | None = None) -> dict[str, Any]:
    octop = octop_root or Path(os.environ.get("OCTOP_REPO", r"E:\git\octop"))
    pa_sha = _run(page_assist_root, "rev-parse", "HEAD") or "UNKNOWN"
    pa_branch = _run(page_assist_root, "rev-parse", "--abbrev-ref", "HEAD") or "UNKNOWN"
    pa_dirty, pa_dirty_hash = _dirty_manifest(page_assist_root)
    oc_sha = _run(octop, "rev-parse", "HEAD") if octop.exists() else None
    oc_dirty, oc_dirty_hash = _dirty_manifest(octop) if octop.exists() else (False, None)
    return {
        "page_assist_baseline": PA_BASELINE,
        "page_assist_implemented_sha": pa_sha,
        "octop_baseline": OC_BASELINE,
        "octop_patched_sha": oc_sha,
        "branch": pa_branch,
        "dirty": pa_dirty or oc_dirty,
        "dirty_manifest_sha256": pa_dirty_hash or oc_dirty_hash,
        "page_assist_sha": pa_sha,
        "octop_baseline_sha": OC_BASELINE,
    }


def missing_live_fields(env: dict[str, Any] | None) -> list[str]:
    required = [
        "instance_role",
        "instance_id",
        "releases_root",
        "state_root",
        "db_identity",
        "python",
        "unit",
        "service_user",
        "expected_exec_argv",
        "public_origin",
        "health_probe",
        "client_registrations",
        "baseline_release",
        "baseline_manifest_sha256",
        "release_manifest",
        "wheelhouse",
        "requirements_lock",
        "config",
        "secret_references",
        "live_test_identities",
    ]
    if not env:
        return required
    missing: list[str] = []
    for field in required:
        value = env.get(field)
        if value in (None, "", [], {}):
            missing.append(field)
    return missing


def load_env_file(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("env-file must be a JSON object")
    return payload
