#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
PA_ROOT = ROOT.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from acceptance.acs import run_ac
from acceptance.catalog import close_ids, fi_close_ids, fi_ids, owner_for
from acceptance.close_acs import run_close_ac
from acceptance.close_fis import run_close_fi
from acceptance.fis import run_fi
from acceptance.source import collect_source, load_env_file, missing_live_fields

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
    "AUTH",
    "SESSION",
    "CATALOG",
    "TURN",
    "RECOVER",
    "HITL",
    "HOST",
    "PACKAGE",
    "DEPLOY",
    "UPGRADE",
    "THREAD",
    "FILE",
    "BRIDGE",
    "SEC",
    "EVID",
]


def python_ids() -> list[str]:
    inherited = [f"A-{d}-{i:03d}" for d in PYTHON_DOMAINS for i in (1, 2, 3)]
    close = [item for item in close_ids() if owner_for(item) == "python"]
    return inherited + close + fi_ids() + fi_close_ids()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def write_run(
    out: Path,
    acceptance_id: str,
    status: str,
    reason: str,
    assertions: list[dict],
    mode: str,
    argv: list[str],
    exit_code: int,
    injection: dict | None = None,
) -> Path:
    run_id = str(uuid4())
    dest = out / acceptance_id / run_id
    dest.mkdir(parents=True, exist_ok=True)
    source = collect_source(PA_ROOT)
    if acceptance_id.startswith("A-CLOSE-"):
        reqs = [f"REQ-CLOSE-{(int(acceptance_id.split('-')[-1]) - 1) // 4 + 1:03d}"]
    elif acceptance_id.startswith("FI-CLOSE-"):
        reqs = ["REQ-CLOSE-012"]
    elif acceptance_id.startswith("FI-"):
        reqs = ["REQ-EVID-001"]
    else:
        req_key = acceptance_id.rsplit("-", 1)[0]
        reqs = [REQ.get(req_key, "REQ-EVID-001")]
    payload = {
        "schema_version": 2,
        "run_id": run_id,
        "acceptance_id": acceptance_id,
        "requirement_ids": reqs,
        "test_ids": [f"TEST-{acceptance_id}"],
        "mode": mode,
        "parameter_case": "default",
        "status": status,
        "reason": reason,
        "source": source,
        "artifact_identity": {
            "browser_sha256": None,
            "module_wheel_sha256": None,
            "host_wheel_sha256": None,
            "release_manifest_sha256": None,
        },
        "scenario": {
            "scenario_id": f"{acceptance_id}:{mode}:default",
            "scenario_plan_sha256": None,
            "subject_release_manifest_sha256": None,
        },
        "phase_observations": [],
        "execution": {
            "command_argv": argv,
            "cwd": str(Path.cwd()),
            "started_at": utcnow(),
            "finished_at": utcnow(),
            "exit_code": exit_code,
            "tool_versions": {"python": sys.version.split()[0]},
            "environment_id": "fixture-local" if mode != "live" else "live",
        },
        "assertions": assertions,
        "state_digests": [],
        "artifacts": [],
        "environment": {"mode": mode},
        "injection": injection,
    }
    run_path = dest / "run.json"
    run_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (dest / "assertions.json").write_text(json.dumps(assertions, ensure_ascii=False, indent=2), encoding="utf-8")
    return run_path


async def run_one(acceptance_id: str, mode: str, env: dict | None) -> tuple[str, str, list[dict], dict | None]:
    if mode == "live":
        missing = missing_live_fields(env)
        live_required = acceptance_id.endswith(
            tuple(
                [
                    "A-CLOSE-005",
                    "A-CLOSE-009",
                    "A-CLOSE-033",
                    "A-CLOSE-041",
                    "A-CLOSE-043",
                    "A-CLOSE-047",
                    "A-DEPLOY-001",
                    "A-DEPLOY-003",
                    "A-EVID-003",
                    "A-HOST-001",
                    "A-BRIDGE-001",
                    "A-BRIDGE-002",
                    "A-BRIDGE-003",
                ]
            )
        ) or acceptance_id in {
            "A-CLOSE-005",
            "A-CLOSE-009",
            "A-CLOSE-033",
            "A-CLOSE-041",
            "A-CLOSE-043",
            "A-CLOSE-047",
            "A-AUTH-001",
            "A-HOST-001",
            "A-THREAD-001",
            "A-TURN-001",
            "A-RECOVER-001",
            "A-HITL-001",
            "A-HITL-003",
            "A-FILE-001",
            "A-BRIDGE-001",
            "A-BRIDGE-002",
            "A-BRIDGE-003",
            "A-UPGRADE-002",
            "A-UPGRADE-003",
            "A-COMPAT-001",
            "A-DEPLOY-001",
            "A-DEPLOY-003",
            "A-EVID-003",
            "FI-CLOSE-005",
            "FI-CLOSE-008",
            "FI-CLOSE-012",
            "FI-CLOSE-013",
            "FI-CLOSE-014",
        }
        if live_required and missing:
            return (
                "BLOCKED",
                "ENVIRONMENT_REQUIRED: " + ",".join(missing),
                [
                    {
                        "name": "environment",
                        "oracle_type": "environment",
                        "passed": False,
                        "expected": "complete deployment-input.json",
                        "actual": missing,
                    }
                ],
                None,
            )
    if acceptance_id.startswith("FI-CLOSE-"):
        status, reason, assertions, injection = await run_close_fi(acceptance_id)
        return status, reason, assertions, injection
    if acceptance_id.startswith("FI-"):
        status, reason, assertions = await run_fi(acceptance_id)
        injection = {"point": acceptance_id, "observed": any(a.get("name") == "injection_observed" and a.get("passed") for a in assertions)}
        return status, reason, assertions, injection
    if acceptance_id.startswith("A-CLOSE-"):
        return await run_close_ac(acceptance_id, mode)
    domain = acceptance_id.split("-")[1]
    if domain in {"CONFIG", "UI", "CLIENT", "DATA", "COMPAT", "CONTEXT", "OBS"}:
        return "BLOCKED", "browser-owned AC; see scripts/enterprise/verify.mjs", [
            {"name": "runner", "passed": False, "expected": "node", "actual": "python"}
        ], None
    status, reason, assertions = await run_ac(acceptance_id)
    return status, reason, assertions, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--acceptance", default="ALL")
    parser.add_argument("--mode", default="fixture", choices=["document", "build", "fixture", "live"])
    parser.add_argument("--output", default=str(PA_ROOT / "artifacts" / "acceptance"))
    parser.add_argument("--env-file", default=None)
    args = parser.parse_args(argv)
    env = load_env_file(args.env_file)
    if args.acceptance == "ALL":
        ids = python_ids()
    elif args.acceptance == "AC":
        ids = [i for i in python_ids() if i.startswith("A-")]
    elif args.acceptance == "FI":
        ids = fi_ids() + fi_close_ids()
    else:
        ids = [args.acceptance]
        if owner_for(ids[0]) == "node" and ids[0] not in python_ids():
            print(json.dumps({"status": "BLOCKED", "reason": "node-owned AC"}))
            return BLOCKED
    out = Path(args.output)
    if not out.is_absolute():
        out = (PA_ROOT / out).resolve()
    index_runs = []
    worst = PASS
    for item in ids:
        status, reason, assertions, injection = asyncio.run(run_one(item, args.mode, env))
        code = {"PASS": PASS, "FAIL": FAIL, "BLOCKED": BLOCKED, "SKIPPED": SKIPPED}[status]
        run_path = write_run(out, item, status, reason, assertions, args.mode, sys.argv, code, injection)
        digest = hashlib.sha256(run_path.read_bytes()).hexdigest()
        index_runs.append(
            {
                "acceptance_id": item,
                "mode": args.mode,
                "parameter_case": "default",
                "run_json": str(run_path),
                "sha256": digest,
                "status": status,
            }
        )
        if code == FAIL:
            worst = FAIL
        elif worst != FAIL and code == BLOCKED:
            worst = BLOCKED
        elif worst == PASS and code == SKIPPED:
            worst = SKIPPED
    index_path = out / "run-index.json"
    source = collect_source(PA_ROOT)
    index_path.write_text(
        json.dumps({"schema_version": 2, "source": source, "runs": index_runs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
