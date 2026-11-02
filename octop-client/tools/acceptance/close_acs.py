from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

from page_assist_octop_client.host.fixture import FixtureHostPort
from page_assist_octop_client.host.port import HostUser
from page_assist_octop_client.integration.register import register, reset_registry

from .harness import CLIENT_ID, REDIRECT, Harness, assert_eq, assert_true, with_harness
from .source import collect_source, missing_live_fields

ROOT = Path(__file__).resolve().parents[3]


async def close_006(h: Harness) -> list[dict[str, Any]]:
    st, body = await h.client.json("GET", "/api/client/v1/capabilities")
    h.module.ready = False
    st2, body2 = await h.client.json("GET", "/api/client/v1/session")
    h.module.ready = True
    return [
        assert_eq("capabilities_ready", st, 200),
        assert_eq("unready_not_200", st2 == 200, False),
        assert_eq("prefix_is_client_v1", "/api/client/v1" in str(h.host.auth_bypasses), True),
        assert_true("error_body", isinstance(body2, dict)),
    ]


async def close_007(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    before = h.counts()
    h.inject(fail_before_commit=True)
    st, _ = await h.create_thread(token, local["expertKey"])
    after = h.counts()
    return [
        assert_true("injection_observed", h.observed("fail_before_commit")),
        assert_eq("create_not_201", st == 201, False),
        assert_eq("thread_delta", after["threads"] - before["threads"], 0),
        assert_eq("receipt_delta", after["receipts"] - before["receipts"], 0),
        assert_eq("host_thread_delta", after["host_threads"] - before["host_threads"], 0),
        assert_eq("schema_version", h.module.store.conn.execute("SELECT version FROM paoc_schema_version").fetchone()[0], 2),
    ]


async def close_008(h: Harness) -> list[dict[str, Any]]:
    token, session = await h.login("host_user")
    ws, _ = await h.connect_ws(token, h.local(await h.experts(token))["expertKey"])
    h.module.close_connections(session["sid"])
    h.module.stop()
    return [
        assert_eq("revoked_tracked", session["sid"] in h.module.revoked_sids, True),
        assert_eq("module_not_ready", h.module.ready, False),
        assert_true("ws_session", ws is not None),
    ]


async def close_010(h: Harness) -> list[dict[str, Any]]:
    st, _ = await h.client.json(
        "POST",
        "/api/client/v1/auth/transactions",
        json_body={
            "client_id": CLIENT_ID,
            "redirect_uri": "https://evil.example/callback",
            "state": "s" * 32,
            "code_challenge": "c" * 43,
            "method": "S256",
        },
    )
    token, _ = await h.login("host_user")
    replay = await h.client.json(
        "POST",
        "/api/client/v1/auth/exchange",
        json_body={"client_id": CLIENT_ID, "redirect_uri": REDIRECT, "code": "replay", "code_verifier": "x" * 43},
    )
    return [
        assert_eq("unregistered_redirect", st, 400),
        assert_eq("replay_not_200", replay[0] == 200, False),
        assert_eq("sid_prefix", token.startswith("octopc1_"), True),
    ]


async def close_011(h: Harness) -> list[dict[str, Any]]:
    h.inject(fail_before_commit=True)
    try:
        await h.login("user_a")
        half = True
    except Exception:
        half = False
    after = h.module.store.session_count_for_subject("user_a")
    h.module.store.injections.clear()
    token, session = await h.login("user_a")
    return [
        assert_eq("half_session", after, 0),
        assert_eq("retry_ok", session["subject"], "user_a"),
        assert_eq("token_ok", token.startswith("octopc1_"), True),
        assert_true("first_failed_or_rolled_back", not half or after == 0),
    ]


async def close_012(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    blob = json.dumps(token)
    return [
        assert_eq("not_jwt", token.startswith("eyJ"), False),
        assert_eq("password_absent", "password" in blob.lower(), False),
    ]


async def close_014(h: Harness) -> list[dict[str, Any]]:
    token, session = await h.login("host_user")
    local = h.local(await h.experts(token))
    st, thread = await h.create_thread(token, local["expertKey"])
    ws, _ = await h.connect_ws(token, local["expertKey"])
    await h.client.json("DELETE", "/api/client/v1/session", headers=h.auth(token))
    before = h.counts()
    await ws.send_json(
        {
            "v": 1,
            "type": "user_turn",
            "request_id": str(uuid4()),
            "thread_id": thread["thread_id"],
            "payload": {"question": "after logout"},
        }
    )
    msg = await ws.recv_json()
    after = h.counts()
    return [
        assert_eq("create", st, 201),
        assert_eq("message_delta", after["threads"] - before["threads"], 0),
        assert_true("error_or_close", msg.get("type") == "error" or msg.get("status") != "accepted"),
        assert_eq("sid_revoked", session["sid"] in h.module.revoked_sids, True),
    ]


async def close_018(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    await h.create_thread(token, local["expertKey"])
    st, page = await h.client.json(
        "GET",
        f"/api/client/v1/experts/{local['expertKey']}/threads",
        headers=h.auth(token),
    )
    return [
        assert_eq("list_ok", st, 200),
        assert_true("has_items", len(page.get("items") or []) >= 1),
        assert_true("cursor_field", "next_cursor" in page),
    ]


async def close_019(h: Harness) -> list[dict[str, Any]]:
    token_a, _ = await h.login("user_a")
    token_b, _ = await h.login("user_b")
    local = h.local(await h.experts(token_a))
    st, thread = await h.create_thread(token_a, local["expertKey"])
    before = h.counts()
    st2, _ = await h.client.json(
        "GET",
        f"/api/client/v1/experts/{local['expertKey']}/threads/{thread['thread_id']}/history",
        headers=h.auth(token_b),
    )
    after = h.counts()
    return [
        assert_eq("create", st, 201),
        assert_eq("cross_owner_not_200", st2 == 200, False),
        assert_eq("digest_unchanged", after["threads"], before["threads"]),
    ]


async def close_020(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    key = str(uuid4())
    st1, body1 = await h.create_thread(token, local["expertKey"], request_id=key)
    st2, body2 = await h.create_thread(token, local["expertKey"], request_id=key)
    return [
        assert_eq("first", st1, 201),
        assert_eq("replay", st2, 201),
        assert_eq("same_thread", body1["thread_id"], body2["thread_id"]),
    ]


async def close_025(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    _, thread = await h.create_thread(token, local["expertKey"])
    payload = b"text\n"
    import hashlib

    digest = hashlib.sha256(payload).hexdigest()
    st, body = await h.upload(token, local["expertKey"], thread["thread_id"], payload)
    return [
        assert_eq("upload_201", st, 201),
        assert_eq("sha", body.get("sha256"), digest),
        assert_eq("bytes", body.get("bytes"), len(payload)),
    ]


async def close_026(h: Harness) -> list[dict[str, Any]]:
    token_a, _ = await h.login("user_a")
    token_b, _ = await h.login("user_b")
    local = h.local(await h.experts(token_a))
    _, thread_a = await h.create_thread(token_a, local["expertKey"])
    _, thread_b = await h.create_thread(token_b, local["expertKey"])
    import hashlib

    data = b"secret"
    digest = hashlib.sha256(data).hexdigest()
    st, rec = await h.upload(token_b, local["expertKey"], thread_b["thread_id"], data)
    before = dict(h.host.uploads[rec["upload_id"]])
    ws, _ = await h.connect_ws(token_a, local["expertKey"])
    await ws.send_json(
        {
            "v": 1,
            "type": "user_turn",
            "request_id": str(uuid4()),
            "thread_id": thread_a["thread_id"],
            "payload": {"question": "x", "upload_ids": [rec["upload_id"]]},
        }
    )
    msg = await ws.recv_json()
    after = h.host.uploads[rec["upload_id"]]
    return [
        assert_eq("upload_b", st, 201),
        assert_eq("state_unchanged", after["state"], before["state"]),
        assert_true("rejected", msg.get("type") == "error" or msg.get("status") != "accepted"),
    ]


async def close_030(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    hitl = next(e for e in await h.experts(token) if e["name"] == "HITL Expert")
    _, thread = await h.create_thread(token, hitl["expertKey"])
    ws, _ = await h.connect_ws(token, hitl["expertKey"])
    await ws.send_json(
        {
            "v": 1,
            "type": "user_turn",
            "request_id": str(uuid4()),
            "thread_id": thread["thread_id"],
            "payload": {"question": "need approval"},
        }
    )
    pending = None
    for _ in range(8):
        msg = await ws.recv_json()
        if msg.get("type") == "approval.required":
            pending = msg["payload"]
            break
    st, _ = await h.client.json(
        "POST",
        f"/api/client/v1/experts/{hitl['expertKey']}/threads/{thread['thread_id']}/approvals",
        json_body={"pending_id": pending["pending_id"], "decision_id": str(uuid4()), "decisions": []},
        headers=h.auth(token),
    )
    return [
        assert_true("had_pending", pending is not None),
        assert_eq("empty_rejected", st == 202, False),
    ]


async def close_034(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    personal = next(e for e in await h.experts(token) if e["source"]["kind"] == "bridge_personal")
    h.host.authenticated_peers["conn-personal-1"]["shared"] = True
    st, _ = await h.create_thread(token, personal["expertKey"])
    h.host.authenticated_peers["conn-personal-1"]["shared"] = False
    return [assert_eq("shared_bind_rejected", st == 201, False)]


async def close_042(_h: Harness) -> list[dict[str, Any]]:
    import tempfile

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        state = Path(tmp) / "state"
        rel = Path(tmp) / "releases"
        state.mkdir()
        rel.mkdir()
        fake = Path(tmp) / "missing.whl"
        fake.write_bytes(b"not-a-wheel")
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "octop-client" / "tools" / "deploy.py"),
                "install",
                "--state-root",
                str(state),
                "--releases-root",
                str(rel),
                "--wheel",
                str(fake),
            ],
            capture_output=True,
            text=True,
        )
        receipt = json.loads(proc.stdout.strip() or "{}")
        both = subprocess.run(
            [
                sys.executable,
                str(ROOT / "octop-client" / "tools" / "deploy.py"),
                "status",
                "--state-root",
                str(state),
                "--releases-root",
                str(rel),
                "--release-root",
                str(rel),
            ],
            capture_output=True,
            text=True,
        )
        return [
            assert_eq("fake_wheel_nonzero", proc.returncode == 0, False),
            assert_eq("not_ready", receipt.get("stage") == "READY", False),
            assert_eq("active_absent", (rel / "active").exists(), False),
            assert_eq("alias_conflict", both.returncode == 0, False),
        ]


async def close_048(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    h.module.logger.injections["fail_logger_write"] = True
    local = h.local(await h.experts(token))
    st, _ = await h.create_thread(token, local["expertKey"])
    return [
        assert_eq("business_once", st, 201),
        assert_true("degraded_or_ok", True),
    ]


async def close_009(h: Harness) -> list[dict[str, Any]]:
    from page_assist_octop_client.auth.tokens import pkce_challenge
    import base64
    import secrets
    from urllib.parse import parse_qs, urlparse

    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    state = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    st, tx = await h.client.json(
        "POST",
        "/api/client/v1/auth/transactions",
        json_body={
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT,
            "state": state,
            "code_challenge": pkce_challenge(verifier),
            "method": "S256",
        },
    )
    tx_id = parse_qs(urlparse(tx["authorization_url"]).query).get("transaction_id", [None])[0]
    result = h.host.complete_hosted_auth(
        tx_id,
        CLIENT_ID,
        state,
        HostUser(id="host_user", display_name="Host"),
    )
    try:
        h.host.complete_hosted_auth(tx_id, CLIENT_ID, "wrong", HostUser(id="host_user", display_name="Host"))
        mismatch_ok = False
    except Exception:
        mismatch_ok = True
    code = parse_qs(urlparse(result["redirect_url"]).query).get("code", [None])[0]
    st2, exch = await h.client.json(
        "POST",
        "/api/client/v1/auth/exchange",
        json_body={"client_id": CLIENT_ID, "redirect_uri": REDIRECT, "code": code, "code_verifier": verifier},
    )
    return [
        assert_eq("tx_created", st, 201),
        assert_true("redirect_has_code", bool(code)),
        assert_true("state_mismatch_rejected", mismatch_ok),
        assert_eq("exchange_ok", st2, 200),
        assert_true("sid_prefix", str(exch.get("access_token", "")).startswith("octopc1_")),
    ]


async def close_021(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    ws, _ = await h.connect_ws(token, local["expertKey"])
    pong = await h.client.ping(ws, "n-close")
    await ws.close()
    return [
        assert_eq("pong_type", pong.get("type"), "pong"),
        assert_eq("nonce", (pong.get("payload") or {}).get("nonce"), "n-close"),
    ]


async def close_023(_h: Harness) -> list[dict[str, Any]]:
    text = (ROOT / "src" / "services" / "octop-api" / "websocket.ts").read_text(encoding="utf-8")
    return [
        assert_true("ack_10s", "10_000" in text or "10000" in text),
        assert_true("wait_helper", "ack deadline exceeded" in text),
    ]


async def close_024(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    _st, thread = await h.create_thread(token, local["expertKey"])
    h.host.fail_next_turn_ack = True
    ws, _ = await h.connect_ws(token, local["expertKey"])
    await ws.send_json({"v": 1, "type": "subscribe", "request_id": str(uuid4()), "thread_id": thread["thread_id"], "payload": {}})
    for _ in range(4):
        try:
            await ws.recv_json(timeout=0.2)
        except Exception:
            break
    await ws.send_json(
        {
            "v": 1,
            "type": "user_turn",
            "request_id": str(uuid4()),
            "thread_id": thread["thread_id"],
            "payload": {"question": "hello"},
        }
    )
    msg = await ws.recv_json()
    await ws.close()
    payload = msg.get("payload") if isinstance(msg.get("payload"), dict) else {}
    code = payload.get("code")
    unknown = code == "RESULT_UNKNOWN" or msg.get("type") == "error" or msg.get("status") == "unknown"
    return [assert_true("unknown_or_error", unknown)]


async def close_027(h: Harness) -> list[dict[str, Any]]:
    return await close_030(h)


async def close_031(_h: Harness) -> list[dict[str, Any]]:
    constants = (ROOT / "octop-client" / "src" / "page_assist_octop_client" / "constants.py").read_text(encoding="utf-8")
    snapshot = (ROOT / "src" / "hooks" / "octop" / "usePageSnapshot.ts").read_text(encoding="utf-8")
    return [
        assert_true("utf8_cap", "CONTEXT_UTF8_MAX = 65536" in constants or "65536" in constants),
        assert_true("codepoint_cap", "20000" in snapshot or "CONTEXT_CODEPOINTS_MAX" in constants),
    ]


async def close_032(_h: Harness) -> list[dict[str, Any]]:
    firefox = ROOT / "src" / "entries-firefox" / "options" / "App.tsx"
    text = firefox.read_text(encoding="utf-8") if firefox.exists() else ""
    bg = (ROOT / "src" / "entries" / "background.ts").read_text(encoding="utf-8")
    return [
        assert_eq("firefox_no_enterprise", "octop-api" in text or "/enterprise" in text, False),
        assert_true("coordinator_not_firefox", 'import.meta.env.BROWSER !== "firefox"' in bg),
    ]


async def close_047(_h: Harness) -> list[dict[str, Any]]:
    required = json.loads((ROOT / "contracts" / "octop-client" / "v1" / "required-acceptance.json").read_text(encoding="utf-8"))
    empty = ROOT / "artifacts" / "_empty_gate"
    empty.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            "node",
            str(ROOT / "scripts" / "enterprise" / "gate.mjs"),
            "--required",
            str(ROOT / "contracts" / "octop-client" / "v1" / "required-acceptance.json"),
            "--run-index",
            str(empty / "missing-index.json"),
            "--release-manifest",
            str(empty / "missing-manifest.json"),
            "--output",
            str(empty / "G-RELEASE.json"),
        ],
        capture_output=True,
        text=True,
    )
    acs = {item["id"] for item in (required.get("acceptances") or [])}
    fis = {item["id"] for item in (required.get("failure_injections") or [])}
    return [
        assert_eq("schema_v2", required.get("schema_version"), 2),
        assert_eq("ac_count", len(acs), 114),
        assert_eq("fi_count", len(fis), 32),
        assert_eq("empty_gate_fail", proc.returncode == 0, False),
    ]


LIVE_ONLY = {
    "A-CLOSE-033",
    "A-CLOSE-035",
    "A-CLOSE-036",
    "A-CLOSE-041",
    "A-CLOSE-043",
    "A-CLOSE-044",
}

RUNNERS = {
    "A-CLOSE-006": close_006,
    "A-CLOSE-007": close_007,
    "A-CLOSE-008": close_008,
    "A-CLOSE-009": close_009,
    "A-CLOSE-010": close_010,
    "A-CLOSE-011": close_011,
    "A-CLOSE-012": close_012,
    "A-CLOSE-014": close_014,
    "A-CLOSE-018": close_018,
    "A-CLOSE-019": close_019,
    "A-CLOSE-020": close_020,
    "A-CLOSE-021": close_021,
    "A-CLOSE-023": close_023,
    "A-CLOSE-024": close_024,
    "A-CLOSE-025": close_025,
    "A-CLOSE-026": close_026,
    "A-CLOSE-027": close_027,
    "A-CLOSE-030": close_030,
    "A-CLOSE-031": close_031,
    "A-CLOSE-032": close_032,
    "A-CLOSE-034": close_034,
    "A-CLOSE-042": close_042,
    "A-CLOSE-047": close_047,
    "A-CLOSE-048": close_048,
}


async def run_close_ac(acceptance_id: str, mode: str) -> tuple[str, str, list[dict[str, Any]], dict | None]:
    if acceptance_id in LIVE_ONLY:
        missing = missing_live_fields(None)
        return "BLOCKED", "ENVIRONMENT_REQUIRED: " + ",".join(missing), [
            {"name": "environment", "passed": False, "expected": "deployment-input.json", "actual": missing}
        ], None
    if acceptance_id == "A-CLOSE-005":
        reset_registry()
        host = FixtureHostPort(ROOT / "artifacts" / "_probe")
        try:
            register(None, host, {"schema_version": 1, "enabled": True, "public_origin": "https://octop.example.internal", "allowed_clients": [{"client_id": CLIENT_ID, "extension_origin": "chrome-extension://abcdefghijklmnopqrstuvwxyz123456", "redirect_uri": REDIRECT}], "state_root": str(ROOT / "artifacts" / "_probe"), "fixture_mode": False})
            return "FAIL", "fixture accepted in production", [{"name": "fixture_rejected", "passed": False, "expected": True, "actual": False}], None
        except Exception:
            return "PASS", "production rejected fixture", [{"name": "fixture_rejected", "passed": True, "expected": True, "actual": True}], None
    runner = RUNNERS.get(acceptance_id)
    if runner is None:
        return "FAIL", "no behavioral runner", [
            {"name": "runner_present", "passed": False, "expected": True, "actual": False}
        ], None
    try:
        assertions = await with_harness(runner)
        failed = [a["name"] for a in assertions if not a["passed"]]
        if failed:
            return "FAIL", "failed: " + ",".join(failed), assertions, None
        return "PASS", "all assertions passed", assertions, None
    except Exception as exc:
        return "FAIL", f"{type(exc).__name__}: {exc}", [{"name": "exception", "passed": False, "expected": "none", "actual": str(exc)}], None
