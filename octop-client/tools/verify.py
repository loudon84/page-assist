#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from acceptance.acs import run_ac
from acceptance.fis import run_fi

PASS, FAIL, BLOCKED, SKIPPED = 0, 1, 2, 3

REQ = {
    "A-CONFIG": "REQ-CONFIG-001",
    "A-AUTH": "REQ-AUTH-001",
    "A-SESSION": "REQ-SESSION-001",
    "A-UI": "REQ-UI-001",
    "A-CATALOG": "REQ-CATALOG-001",
    "A-CLIENT": "REQ-CLIENT-001",
    "A-HOST": "REQ-HOST-001",
    "A-PACKAGE": "REQ-PACKAGE-001",
    "A-DEPLOY": "REQ-DEPLOY-001",
    "A-UPGRADE": "REQ-UPGRADE-001",
    "A-THREAD": "REQ-THREAD-001",
    "A-TURN": "REQ-TURN-001",
    "A-RECOVER": "REQ-RECOVER-001",
    "A-HITL": "REQ-HITL-001",
    "A-CONTEXT": "REQ-CONTEXT-001",
    "A-FILE": "REQ-FILE-001",
    "A-DATA": "REQ-DATA-001",
    "A-BRIDGE": "REQ-BRIDGE-001",
    "A-COMPAT": "REQ-COMPAT-001",
    "A-SEC": "REQ-SEC-001",
    "A-OBS": "REQ-OBS-001",
    "A-EVID": "REQ-EVID-001",
}

PYTHON_DOMAINS = [
    "AUTH", "SESSION", "CATALOG", "TURN", "RECOVER", "HITL",
    "HOST", "PACKAGE", "DEPLOY", "UPGRADE", "THREAD", "FILE", "BRIDGE", "SEC", "EVID",
]
BROWSER_DOMAINS = ["CONFIG", "UI", "CLIENT", "DATA", "COMPAT", "CONTEXT", "OBS"]
FI_IDS = [f"FI-{i:02d}" for i in range(1, 17)]


def all_ac_ids() -> list[str]:
    domains = [
        "CONFIG", "AUTH", "SESSION", "UI", "CATALOG", "CLIENT", "HOST", "PACKAGE",
        "DEPLOY", "UPGRADE", "THREAD", "TURN", "RECOVER", "HITL", "CONTEXT", "FILE",
        "DATA", "BRIDGE", "COMPAT", "SEC", "OBS", "EVID",
    ]
    return [f"A-{d}-{i:03d}" for d in domains for i in (1, 2, 3)]


def python_ids() -> list[str]:
    return [f"A-{d}-{i:03d}" for d in PYTHON_DOMAINS for i in (1, 2, 3)] + FI_IDS


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def write_run(out: Path, acceptance_id: str, status: str, reason: str, assertions: list[dict], mode: str, argv: list[str], exit_code: int) -> None:
    run_id = str(uuid4())
    dest = out / acceptance_id / run_id
    dest.mkdir(parents=True, exist_ok=True)
    req_key = acceptance_id.rsplit("-", 1)[0] if acceptance_id.startswith("A-") else "A-EVID"
    payload = {
        "schema_version": 1,
        "run_id": run_id,
        "acceptance_id": acceptance_id,
        "requirement_ids": [REQ.get(req_key, "REQ-EVID-001")],
        "test_id": f"TEST-{acceptance_id}",
        "mode": mode,
        "status": status,
        "reason": reason,
        "source": {
            "page_assist_sha": "2c286d949d30a7667437b796513c09b69e0a98a6",
            "octop_baseline_sha": "e3041c452ffc870f754378bd99d964349580d3f9",
            "octop_patched_sha": None,
            "branch": "main",
            "dirty": True,
            "dirty_manifest_sha256": None,
        },
        "artifacts_identity": {
            "browser_sha256": None,
            "wheel_sha256": None,
            "release_manifest_sha256": None,
        },
        "execution": {
            "command_argv": argv,
            "cwd": str(Path.cwd()),
            "started_at": utcnow(),
            "finished_at": utcnow(),
            "exit_code": exit_code,
            "tool_versions": {"python": sys.version.split()[0]},
            "environment_id": "fixture-local",
        },
        "assertions": assertions,
        "state_digests": [],
        "artifacts": [],
    }
    (dest / "run.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


async def run_one(acceptance_id: str) -> tuple[str, str, list[dict]]:
    if acceptance_id.startswith("FI-"):
        return await run_fi(acceptance_id)
    domain = acceptance_id.split("-")[1]
    if domain in BROWSER_DOMAINS:
        return "BLOCKED", "browser-owned AC; see scripts/enterprise/verify.mjs", [
            {"name": "runner", "passed": False, "expected": "node", "actual": "python"}
        ]
    return await run_ac(acceptance_id)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--acceptance", default="ALL")
    parser.add_argument("--mode", default="fixture", choices=["fixture", "live", "document"])
    parser.add_argument("--output", default="artifacts/acceptance")
    args = parser.parse_args(argv)
    if args.acceptance == "ALL":
        ids = python_ids()
    elif args.acceptance == "AC":
        ids = [i for i in python_ids() if i.startswith("A-")]
    elif args.acceptance == "FI":
        ids = FI_IDS
    else:
        ids = [args.acceptance]
    out = Path(args.output)
    worst = PASS
    for item in ids:
        if args.mode == "live" and item != "A-EVID-003":
            status, reason, assertions = "BLOCKED", "live mode reserved for A-EVID-003", [
                {"name": "environment", "passed": False, "expected": "available", "actual": "unavailable"}
            ]
        else:
            status, reason, assertions = asyncio.run(run_one(item))
        code = {"PASS": PASS, "FAIL": FAIL, "BLOCKED": BLOCKED, "SKIPPED": SKIPPED}[status]
        write_run(out, item, status, reason, assertions, args.mode, sys.argv, code)
        if code == FAIL:
            worst = FAIL
        elif worst != FAIL and code == BLOCKED:
            worst = BLOCKED
        elif worst == PASS and code == SKIPPED:
            worst = SKIPPED
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
