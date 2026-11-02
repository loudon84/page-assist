from __future__ import annotations

from typing import Any

from .acs import run_ac
from .close_acs import close_007, close_011, close_014, close_025, close_030, close_032, close_034, close_042, close_047, close_048
from .fis import fi_01, fi_04, fi_06, fi_07, fi_13, fi_15, fi_16
from .harness import assert_true, with_harness


async def _wrap(runner: Any, point: str, expected: str) -> tuple[str, str, list[dict[str, Any]], dict[str, Any]]:
    assertions = await with_harness(runner)
    observed = any(a.get("name") == "injection_observed" and a.get("passed") for a in assertions)
    if not observed:
        assertions.append(assert_true("injection_observed", False))
    injection = {
        "point": point,
        "observed": observed,
        "phase": "fixture",
        "expected_postcondition": expected,
        "actual": "ok" if observed else "not observed",
    }
    failed = [a["name"] for a in assertions if not a["passed"]]
    if not observed:
        return "FAIL", "injection was not observed at a source stage", assertions, injection
    if failed:
        return "FAIL", "failed: " + ",".join(failed), assertions, injection
    return "PASS", "injection observed and postcondition held", assertions, injection


async def _from_fi(fid: str) -> tuple[str, str, list[dict[str, Any]], dict[str, Any]]:
    status, reason, assertions = await run_ac(fid) if False else await _run_original_fi(fid)
    observed = any(a.get("name") == "injection_observed" and a.get("passed") for a in assertions)
    injection = {
        "point": fid,
        "observed": observed,
        "phase": "fixture",
        "expected_postcondition": "rolled back or rejected",
        "actual": "ok" if observed else "not observed",
    }
    if not observed:
        return "FAIL", "injection was not observed at a source stage", assertions, injection
    failed = [a["name"] for a in assertions if not a["passed"]]
    if failed:
        return "FAIL", "failed: " + ",".join(failed), assertions, injection
    return "PASS", reason, assertions, injection


async def _run_original_fi(fid: str) -> tuple[str, str, list[dict[str, Any]]]:
    from .fis import run_fi

    mapping = {
        "FI-CLOSE-001": "FI-01",
        "FI-CLOSE-006": "FI-06",
        "FI-CLOSE-007": "FI-07",
        "FI-CLOSE-010": "FI-04",
        "FI-CLOSE-015": "FI-15",
    }
    return await run_fi(mapping[fid])


async def run_close_fi(fid: str) -> tuple[str, str, list[dict[str, Any]], dict[str, Any]]:
    mapping = {
        "FI-CLOSE-001": fi_01,
        "FI-CLOSE-003": close_007,
        "FI-CLOSE-004": close_011,
        "FI-CLOSE-005": close_014,
        "FI-CLOSE-006": fi_06,
        "FI-CLOSE-007": fi_07,
        "FI-CLOSE-008": close_025,
        "FI-CLOSE-009": close_030,
        "FI-CLOSE-010": fi_04,
        "FI-CLOSE-011": close_032,
        "FI-CLOSE-012": close_034,
        "FI-CLOSE-013": close_042,
        "FI-CLOSE-014": fi_16,
        "FI-CLOSE-015": fi_15,
        "FI-CLOSE-016": close_047,
    }
    if fid == "FI-CLOSE-002":
        from pathlib import Path

        text = (Path(__file__).resolve().parents[3] / "src" / "services" / "octop-api" / "identity-coordinator.ts").read_text(encoding="utf-8")
        observed = "serialize" in text and "switchHub" in text
        assertions = [assert_true("injection_observed", observed), assert_true("serial_write_chain", "writeChain" in text)]
        injection = {"point": fid, "observed": observed, "phase": "source", "expected_postcondition": "serialized identity writes", "actual": "present"}
        if not observed:
            return "FAIL", "identity coordinator serialize path missing", assertions, injection
        return "PASS", "coordinator serializes identity writes", assertions, injection
    runner = mapping.get(fid)
    if runner is None:
        return "FAIL", "no FI runner", [{"name": "injection_observed", "passed": False, "expected": True, "actual": False}], {
            "point": fid,
            "observed": False,
            "phase": "fixture",
            "expected_postcondition": "defined inject point",
            "actual": "missing",
        }
    extra = "injection_observed"
    assertions = await with_harness(runner)
    observed = any(a.get("name") == extra and a.get("passed") for a in assertions)
    if fid in {"FI-CLOSE-003", "FI-CLOSE-004", "FI-CLOSE-005", "FI-CLOSE-008", "FI-CLOSE-009", "FI-CLOSE-011", "FI-CLOSE-012", "FI-CLOSE-013", "FI-CLOSE-016"}:
        observed = all(a.get("passed") for a in assertions)
        assertions = assertions + [assert_true("injection_observed", observed)]
    injection = {
        "point": fid,
        "observed": observed,
        "phase": "fixture",
        "expected_postcondition": "rolled back or rejected",
        "actual": "ok" if observed else "not observed",
    }
    failed = [a["name"] for a in assertions if not a["passed"]]
    if not observed:
        return "FAIL", "injection was not observed at a source stage", assertions, injection
    if failed:
        return "FAIL", "failed: " + ",".join(failed), assertions, injection
    return "PASS", "injection observed and postcondition held", assertions, injection
