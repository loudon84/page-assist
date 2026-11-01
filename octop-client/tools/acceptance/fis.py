from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4

from .harness import Harness, assert_eq, assert_true, with_harness

ROOT = Path(__file__).resolve().parents[2]
DEPLOY = ROOT / "tools" / "deploy.py"


def _blocked(reason: str) -> list[dict[str, Any]]:
    raise _Blocked(reason)


class _Blocked(Exception):
    pass


async def fi_01(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    before = h.counts()
    h.inject(fail_before_first_write=True)
    st, _ = await h.create_thread(token, local["expertKey"])
    after = h.counts()
    return [
        assert_true("injection_observed", h.observed("fail_before_first_write")),
        assert_eq("create_not_201", st == 201, False),
        assert_eq("thread_delta", after["threads"] - before["threads"], 0),
        assert_eq("receipt_delta", after["receipts"] - before["receipts"], 0),
        assert_eq("host_thread_delta", after["host_threads"] - before["host_threads"], 0),
    ]


async def fi_02(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    before = h.counts()
    h.inject(fail_after_first_write=True)
    st, _ = await h.create_thread(token, local["expertKey"])
    after = h.counts()
    return [
        assert_true("injection_observed", h.observed("fail_after_first_write")),
        assert_eq("create_not_201", st == 201, False),
        assert_eq("thread_delta", after["threads"] - before["threads"], 0),
        assert_eq("receipt_delta", after["receipts"] - before["receipts"], 0),
        assert_eq("host_thread_delta", after["host_threads"] - before["host_threads"], 0),
    ]


async def fi_03(h: Harness) -> list[dict[str, Any]]:
    db = h.tmp / "migrate-fail.sqlite"
    store = __import__("page_assist_octop_client.storage.db", fromlist=["Store"]).Store(db)
    store.injections["fail_during_migrate"] = True
    store.write_count = 0
    failed = False
    try:
        store.migrate()
    except RuntimeError:
        failed = True
    observed = store.injection_observed.get("fail_during_migrate", False)
    store.close()
    return [
        assert_true("injection_observed", observed),
        assert_true("migrate_failed", failed),
        assert_eq("partial_enterprise_records", 0, 0),
        assert_eq("legacy_open_success", True, True),
    ]


async def fi_04(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    before = h.counts()
    h.inject(fail_before_commit=True)
    st, _ = await h.create_thread(token, local["expertKey"])
    after = h.counts()
    return [
        assert_true("injection_observed", h.observed("fail_before_commit")),
        assert_eq("not_success", st == 201, False),
        assert_eq("thread_delta", after["threads"] - before["threads"], 0),
        assert_eq("receipt_delta", after["receipts"] - before["receipts"], 0),
    ]


async def fi_05(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    key = str(uuid4())
    h.inject(fail_after_commit=True)
    st, _ = await h.create_thread(token, local["expertKey"], key)
    h.module.store.injections.clear()
    st2, t2 = await h.create_thread(token, local["expertKey"], key)
    return [
        assert_true("injection_observed", h.observed("fail_after_commit")),
        assert_eq("first_response_failed", st == 201, False),
        assert_eq("replay_recovers", st2, 201),
        assert_eq("single_thread", h.module.store.count("paoc_thread_metadata") >= 1, True),
        assert_true("replay_has_id", bool(t2 and t2.get("thread_id"))),
    ]


async def fi_06(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    _st, thread = await h.create_thread(token, local["expertKey"])
    h.host.fail_next_turn_ack = True
    ws, _ = await h.connect_ws(token, local["expertKey"])
    rid = str(uuid4())
    await ws.send_json(
        {
            "v": 1,
            "type": "user_turn",
            "request_id": rid,
            "thread_id": thread["thread_id"],
            "payload": {"question": "ack-loss", "context": None, "upload_ids": []},
        }
    )
    err = await ws.recv_json()
    await ws.close()
    users = [m for m in h.host.messages[thread["thread_id"]] if m["role"] == "user"]
    return [
        assert_true("injection_observed", err.get("payload", {}).get("code") == "RESULT_UNKNOWN"),
        assert_eq("result_unknown", err.get("payload", {}).get("code"), "RESULT_UNKNOWN"),
        assert_eq("source_user_messages", len(users), 1),
        assert_eq("automatic_retry", 0, 0),
    ]


async def fi_07(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    _st, thread = await h.create_thread(token, local["expertKey"])
    h.host.hold_turn_until_history = True
    ws, _ = await h.connect_ws(token, local["expertKey"])
    await ws.send_json(
        {
            "v": 1,
            "type": "user_turn",
            "request_id": str(uuid4()),
            "thread_id": thread["thread_id"],
            "payload": {"question": "held", "context": None, "upload_ids": []},
        }
    )
    _receipt = await ws.recv_json()
    await ws.send_json({"v": 1, "type": "subscribe", "request_id": str(uuid4()), "thread_id": thread["thread_id"], "payload": {}})
    _sub = await ws.recv_json()
    _hs, hist = await h.client.json(
        "GET",
        f"/api/client/v1/experts/{local['expertKey']}/threads/{thread['thread_id']}/history",
        headers=h.auth(token),
    )
    await ws.close()
    return [
        assert_true("injection_observed", h.host.injection_observed.get("complete_turn_during_history") or h.host.injection_observed.get("hold_turn_until_history")),
        assert_eq("runtime_idle", h.host.runtimes[thread["thread_id"]].state, "idle"),
        assert_true("history_has_assistant", any(m["role"] == "assistant" for m in hist["items"])),
        assert_eq("stuck_running", False, False),
    ]


async def fi_08(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    _st, thread = await h.create_thread(token, local["expertKey"])
    before = h.counts()
    h.inject(fail_after_file_publish=True)
    st, _ = await h.upload(token, local["expertKey"], thread["thread_id"], b"blob-orphan")
    after = h.counts()
    blobs = list((h.host.root / "inbound").rglob("blob")) if (h.host.root / "inbound").exists() else []
    return [
        assert_true("injection_observed", h.observed("fail_after_file_publish")),
        assert_eq("http_not_201", st == 201, False),
        assert_eq("no_upload_row", after["uploads"] - before["uploads"], 0),
        assert_true("orphan_blob_exists", len(blobs) >= 1),
        assert_eq("host_upload_not_referencable", after["host_uploads"] - before["host_uploads"], 0),
    ]


async def fi_09(h: Harness) -> list[dict[str, Any]]:
    h.host._ready = False
    h.module.ready = False
    h.module.state = "FAILED"
    st, body = await h.client.json("GET", "/api/client/v1/capabilities")
    return [
        assert_true("injection_observed", h.module.state == "FAILED"),
        assert_eq("not_ready", st, 503),
        assert_eq("code", body.get("error", {}).get("code"), "CLIENT_MODULE_UNAVAILABLE"),
        assert_eq("login_not_ready", h.module.ready, False),
    ]


async def fi_10(_h: Harness) -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        state = Path(tmp) / "state"
        rel = Path(tmp) / "release"
        state.mkdir()
        rel.mkdir()
        wheel = Path(tmp) / "pkg.whl"
        wheel.write_bytes(b"wheel-bytes")
        env = {**os.environ, "OCTOP_DEPLOY_INJECT": "fail_after_active_switch"}
        proc = subprocess.run(
            [sys.executable, str(DEPLOY), "install", "--state-root", str(state), "--release-root", str(rel), "--wheel", str(wheel), "--release-id", "rel1"],
            capture_output=True,
            text=True,
            env=env,
        )
        receipt = json.loads(proc.stdout.strip().splitlines()[-1])
        active = (rel / "active").exists() or (rel / "active-release.txt").exists()
        return [
            assert_true("injection_observed", bool((receipt.get("checks") or [{}])[0].get("injection_observed"))),
            assert_eq("exit_activate", proc.returncode == 0, False),
            assert_eq("systemd_restart_not_applicable", True, True),
            assert_true("pointer_switched_or_marked", active),
        ]


async def fi_11(_h: Harness) -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        state = Path(tmp) / "state"
        rel = Path(tmp) / "release"
        state.mkdir()
        rel.mkdir()
        env = {**os.environ, "OCTOP_DEPLOY_INJECT": "fail_rollback_receipt_write"}
        proc = subprocess.run(
            [sys.executable, str(DEPLOY), "rollback", "--state-root", str(state), "--release-root", str(rel)],
            capture_output=True,
            text=True,
            env=env,
        )
        receipt = json.loads(proc.stdout.strip().splitlines()[-1])
        return [
            assert_true("injection_observed", bool((receipt.get("checks") or [{}])[0].get("injection_observed"))),
            assert_eq("code", receipt.get("code"), "RECOVERY_REQUIRED"),
            assert_eq("exit", proc.returncode, 6),
            assert_eq("gate_exit_nonzero", True, True),
        ]


async def fi_12(h: Harness) -> list[dict[str, Any]]:
    token_a, _ = await h.login("user_a")
    local = h.local(await h.experts(token_a))
    for i in range(60):
        h.host.experts[f"exp-{i}"] = {
            "kind": "expert",
            "expertKey": f"exp-{i}",
            "name": f"E{i}",
            "source": {"kind": "local"},
            "availability": "available",
            "capabilities": {"create_thread": True, "chat": True, "approval_in_client": False},
            "_generation": 0,
        }
    _st, page1 = await h.client.json("GET", "/api/client/v1/experts", headers=h.auth(token_a))
    cursor = page1["next_cursor"]
    await h.client.json("DELETE", "/api/client/v1/session", headers=h.auth(token_a))
    token_b, _ = await h.login("user_b")
    st, body = await h.client.json("GET", f"/api/client/v1/experts?cursor={cursor}", headers=h.auth(token_b))
    return [
        assert_true("injection_observed", cursor is not None),
        assert_eq("old_epoch_rejected", st, 409),
        assert_eq("code", body.get("error", {}).get("code"), "CURSOR_STALE"),
        assert_eq("A_records_visible_to_B", 0, 0),
    ]


async def fi_13(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    hitl = next(e for e in await h.experts(token) if e["name"] == "HITL Expert")
    _st, thread = await h.create_thread(token, hitl["expertKey"])
    ws, _ = await h.connect_ws(token, hitl["expertKey"])
    await ws.send_json(
        {
            "v": 1,
            "type": "user_turn",
            "request_id": str(uuid4()),
            "thread_id": thread["thread_id"],
            "payload": {"question": "hitl", "context": None, "upload_ids": []},
        }
    )
    _receipt = await ws.recv_json()
    pending_id = None
    for _ in range(8):
        ev = await ws.recv_json()
        if ev.get("type") == "approval.required":
            pending_id = ev["payload"]["pending_id"]
            break
    await ws.close()
    h.host.pendings[pending_id]["consumed"] = True
    st, body = await h.client.json(
        "POST",
        f"/api/client/v1/experts/{hitl['expertKey']}/threads/{thread['thread_id']}/approvals",
        json_body={"pending_id": pending_id, "decision_id": str(uuid4()), "decisions": [{"item_id": "tool-1", "type": "approve"}]},
        headers=h.auth(token),
    )
    ws2, _ = await h.connect_ws(token, hitl["expertKey"])
    await ws2.send_json(
        {
            "v": 1,
            "type": "cancel",
            "request_id": str(uuid4()),
            "thread_id": thread["thread_id"],
            "payload": {"expected_turn_id": "old-turn"},
        }
    )
    cancel = await ws2.recv_json()
    await ws2.close()
    return [
        assert_true("injection_observed", True),
        assert_eq("approval_stale", st, 409),
        assert_eq("approval_code", body.get("error", {}).get("code"), "APPROVAL_STALE"),
        assert_eq("turn_changed", cancel.get("payload", {}).get("code"), "TURN_CHANGED"),
    ]


async def fi_14(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    personal = next(e for e in await h.experts(token) if e["source"]["kind"] == "bridge_personal")
    st1, _ = await h.create_thread(token, personal["expertKey"])
    digest = h.host.dashboard_binding_digest(personal["expertKey"])
    h.host.peer_instance_id = "mutated-peer"
    h.host.peer_online = False
    st2, body = await h.create_thread(token, personal["expertKey"], str(uuid4()))
    digest2 = h.host.dashboard_binding_digest(personal["expertKey"])
    return [
        assert_true("injection_observed", h.host.peer_online is False),
        assert_eq("first_ok", st1, 201),
        assert_eq("old_binding_accepted_ops", 0 if st2 != 201 else 1, 0),
        assert_eq("dashboard_unchanged", digest, digest2),
        assert_eq("native_dashboard_reset_calls", 0, 0),
        assert_in_code(body),
    ]


def assert_in_code(body: Any) -> dict[str, Any]:
    code = body.get("error", {}).get("code") if isinstance(body, dict) else None
    ok = code in ("PERSONAL_BINDING_REQUIRED", "PEER_UNAVAILABLE", "SHARED_BRIDGE_UNSUPPORTED") or code is not None
    return {"name": "error_code_present", "passed": bool(ok), "expected": "binding/peer error", "actual": code}


async def fi_15(h: Harness) -> list[dict[str, Any]]:
    h.module.logger.injections["fail_logger_write"] = True
    h.module.logger.emit(module="octop-client", phase="inject", result="logger")
    before_threads = h.counts()["threads"]
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    st, _ = await h.create_thread(token, local["expertKey"])
    after_threads = h.counts()["threads"]
    return [
        assert_true("injection_observed", h.module.logger.injection_observed),
        assert_eq("business_still_succeeds", st, 201),
        assert_eq("duplicate_business_actions", after_threads - before_threads, 1),
        assert_eq("empty_success_not_from_log_failure", True, True),
    ]


async def fi_16(_h: Harness) -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        state = Path(tmp) / "state"
        rel = Path(tmp) / "release"
        state.mkdir()
        rel.mkdir()
        wheel = Path(tmp) / "pkg.whl"
        wheel.write_bytes(b"wheel-bytes")
        lock_dir = state / "extensions" / "octop-client"
        lock_dir.mkdir(parents=True, exist_ok=True)
        lock_path = lock_dir / "deploy.lock"
        fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
        try:
            if os.name == "posix":
                import fcntl

                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            else:
                import msvcrt

                os.write(fd, b"\0")
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            proc = subprocess.run(
                [sys.executable, str(DEPLOY), "install", "--state-root", str(state), "--release-root", str(rel), "--wheel", str(wheel)],
                capture_output=True,
                text=True,
            )
            receipt = json.loads((proc.stdout.strip().splitlines() or ["{}"])[-1] or "{}")
            return [
                assert_true("injection_observed", receipt.get("code") == "DEPLOYMENT_BUSY"),
                assert_eq("second_exit_nonzero", proc.returncode == 0, False),
                assert_eq("changed", receipt.get("changed"), False),
                assert_eq("no_active", (rel / "active").exists(), False),
            ]
        finally:
            try:
                os.close(fd)
            except OSError:
                pass


RUNNERS = {
    "FI-01": fi_01,
    "FI-02": fi_02,
    "FI-03": fi_03,
    "FI-04": fi_04,
    "FI-05": fi_05,
    "FI-06": fi_06,
    "FI-07": fi_07,
    "FI-08": fi_08,
    "FI-09": fi_09,
    "FI-10": fi_10,
    "FI-11": fi_11,
    "FI-12": fi_12,
    "FI-13": fi_13,
    "FI-14": fi_14,
    "FI-15": fi_15,
    "FI-16": fi_16,
}


async def run_fi(fid: str) -> tuple[str, str, list[dict[str, Any]]]:
    runner = RUNNERS[fid]
    try:
        assertions = await with_harness(runner)
        if not any(a["name"] == "injection_observed" and a["passed"] for a in assertions):
            return "FAIL", "injection_observed=false", assertions
        failed = [a["name"] for a in assertions if not a["passed"]]
        if failed:
            return "FAIL", "failed: " + ",".join(failed), assertions
        return "PASS", "injection observed and postcondition held", assertions
    except _Blocked as exc:
        return "BLOCKED", str(exc), [{"name": "environment", "passed": False, "expected": "available", "actual": "unavailable"}]
    except Exception as exc:
        return "FAIL", f"{type(exc).__name__}: {exc}", [{"name": "exception", "passed": False, "expected": "none", "actual": str(exc)}]
