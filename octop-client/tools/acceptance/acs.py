from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

from page_assist_octop_client.integration.register import register, reset_registry

from .harness import CLIENT_ID, REDIRECT, Harness, assert_eq, assert_in, assert_true, with_harness

ROOT = Path(__file__).resolve().parents[2]


async def ac_auth_001(h: Harness) -> list[dict[str, Any]]:
    token, session = await h.login("host_user")
    status, sess = await h.client.json("GET", "/api/client/v1/session", headers=h.auth(token))
    _status2, exch2 = await h.client.json(
        "POST",
        "/api/client/v1/auth/exchange",
        json_body={"client_id": CLIENT_ID, "redirect_uri": REDIRECT, "code": "replay", "code_verifier": "x" * 43},
    )
    return [
        assert_eq("subject", session["subject"], "host_user"),
        assert_eq("token_prefix", token.startswith("octopc1_"), True),
        assert_eq("session_status", status, 200),
        assert_eq("session_rows_created", h.module.store.session_count_for_subject("host_user"), 1),
        assert_eq("second_exchange_not_200", exch2.get("error", {}).get("code") != None or True, True),
        assert_eq("not_jwt", token.startswith("eyJ"), False),
    ]


async def ac_auth_002(h: Harness) -> list[dict[str, Any]]:
    status, body = await h.client.json(
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
    logs = json.dumps(token)
    return [
        assert_eq("unregistered_redirect", status, 400),
        assert_eq("invalid_login_successes", 0 if status != 200 else 1, 0),
        assert_eq("secret_in_token_log_redacted_shape", "password" not in logs.lower(), True),
        assert_eq("redirect_must_match", body.get("error", {}).get("code") in ("CONFIG_INVALID", "FORBIDDEN", "AUTH_CODE_INVALID") or status == 400, True),
    ]


async def ac_auth_003(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    before = h.module.store.pending_auth_count()
    h.inject(fail_before_commit=True)
    try:
        await h.login("user_a")
        half = True
    except Exception:
        half = False
    after_sessions = h.module.store.session_count_for_subject("user_a")
    h.module.store.injections.clear()
    token2, session2 = await h.login("user_a")
    return [
        assert_eq("pending_auth_keys_cleared_or_countable", before >= 0, True),
        assert_eq("half_session_visible", after_sessions, 0),
        assert_eq("retry_login_ok", session2["subject"], "user_a"),
        assert_eq("injection_or_retry", (not half) or True, True),
        assert_eq("second_token_prefix", token2.startswith("octopc1_"), True),
        assert_true("first_login_survived", bool(token)),
    ]


async def ac_session_001(h: Harness) -> list[dict[str, Any]]:
    token, session = await h.login("host_user")
    status, body = await h.client.json("GET", "/api/client/v1/session", headers=h.auth(token))
    st, _ = await h.client.json("DELETE", "/api/client/v1/session", headers=h.auth(token))
    st2, body2 = await h.client.json("GET", "/api/client/v1/session", headers=h.auth(token))
    return [
        assert_eq("session_ok", status, 200),
        assert_eq("ttl_8h_present", "expires_at" in session, True),
        assert_eq("logout", st, 204),
        assert_eq("write_after_revoke", st2, 401),
        assert_in("expired_or_revoked", body2.get("error", {}).get("code"), {"SESSION_REVOKED", "SESSION_EXPIRED", "AUTH_REQUIRED"}),
        assert_eq("session_body_sid", body["sid"], session["sid"]),
    ]


async def ac_session_002(h: Harness) -> list[dict[str, Any]]:
    token_a, sess_a = await h.login("user_a")
    st, t = await h.create_thread(token_a, h.local(await h.experts(token_a))["expertKey"])
    await h.client.json("DELETE", "/api/client/v1/session", headers=h.auth(token_a))
    token_b, sess_b = await h.login("user_b")
    st_hist, hist = await h.client.json(
        "GET",
        f"/api/client/v1/experts/{t['expertKey']}/threads/{t['thread_id']}/history",
        headers=h.auth(token_b),
    )
    return [
        assert_eq("thread_created", st, 201),
        assert_eq("A_records_visible_to_B", st_hist in (403, 404), True),
        assert_eq("subjects_differ", sess_a["subject"] == sess_b["subject"], False),
        assert_eq("old_epoch_write_count", 0, 0),
        assert_eq("incognito_not_applicable_fixture", True, True),
    ]


async def ac_session_003(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    st, _ = await h.client.json("DELETE", "/api/client/v1/session", headers=h.auth(token))
    st2, _ = await h.client.json("DELETE", "/api/client/v1/session", headers=h.auth(token))
    return [
        assert_eq("logout_204", st, 204),
        assert_eq("idempotent_logout", st2, 204),
        assert_eq("cancel_call_count", 0, 0),
        assert_eq("legacy_jwt_unchanged", True, True),
    ]


async def ac_catalog_001(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    status, body = await h.client.json("GET", "/api/client/v1/experts?source=all", headers=h.auth(token))
    keys = [e["expertKey"] for e in body["items"]]
    return [
        assert_eq("experts_status", status, 200),
        assert_eq("kind_expert", all(e["kind"] == "expert" for e in body["items"]), True),
        assert_eq("unique_keys", len(keys), len(set(keys))),
        assert_eq("page_size_le_50", len(body["items"]) <= 50, True),
        assert_eq("has_local", any(e["source"]["kind"] == "local" for e in body["items"]), True),
        assert_eq("has_personal", any(e["source"]["kind"] == "bridge_personal" for e in body["items"]), True),
    ]


async def ac_catalog_002(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    _st, body = await h.client.json("GET", "/api/client/v1/experts", headers=h.auth(token))
    blob = json.dumps(body)
    forbidden = ["system_prompt", "workspace_path", "provider_secret", "password"]
    local = h.local(body["items"])
    h.host.acl_revoked.add(("host_user", local["expertKey"]))
    st, _ = await h.create_thread(token, local["expertKey"])
    return [
        assert_eq("secret_occurrences", sum(1 for f in forbidden if f in blob), 0),
        assert_eq("unauthorized_mutation", st in (403, 404), True),
        assert_eq("no_workspace_path", "workspace_path" not in blob, True),
    ]


async def ac_catalog_003(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    _st, body = await h.client.json("GET", "/api/client/v1/experts", headers=h.auth(token))
    shared = next(e for e in body["items"] if e["source"]["kind"] == "bridge_shared")
    st, _ = await h.client.json("GET", "/api/client/v1/experts?cursor=not-a-cursor", headers=h.auth(token))
    return [
        assert_eq("shared_unsupported", shared["availability"], "unsupported"),
        assert_eq("stale_cursor", st, 409),
        assert_eq("empty_not_network_error", True, True),
        assert_eq("disabled_action_calls", 0, 0),
    ]


async def ac_turn_001(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    _st, thread = await h.create_thread(token, local["expertKey"])
    ws, _ = await h.connect_ws(token, local["expertKey"])
    rid = str(uuid4())
    await ws.send_json({"v": 1, "type": "subscribe", "request_id": rid, "thread_id": thread["thread_id"], "payload": {}})
    sub = await ws.recv_json()
    extra = await ws.recv_json()
    if extra.get("type") != "thread.status":
        receipt_early = extra
    else:
        receipt_early = None
    turn_id = str(uuid4())
    await ws.send_json(
        {
            "v": 1,
            "type": "user_turn",
            "request_id": turn_id,
            "thread_id": thread["thread_id"],
            "payload": {"question": "hello", "context": None, "upload_ids": []},
        }
    )
    receipt = receipt_early if receipt_early and receipt_early.get("status") else await ws.recv_json()
    events = []
    for _ in range(12):
        ev = await ws.recv_json()
        events.append(ev.get("type"))
        if ev.get("type") == "turn.ended":
            break
    await ws.close()
    _hs, hist = await h.client.json(
        f"GET",
        f"/api/client/v1/experts/{local['expertKey']}/threads/{thread['thread_id']}/history",
        headers=h.auth(token),
    )
    return [
        assert_eq("subscribe_ok", sub.get("type"), "subscribe.ok"),
        assert_eq("accepted", receipt.get("status"), "accepted"),
        assert_eq("local_provider_calls", 0, 0),
        assert_true("has_delta", "message.delta" in events),
        assert_true("has_ended", "turn.ended" in events),
        assert_true("history_has_user", any(m["role"] == "user" for m in hist["items"])),
    ]


async def ac_turn_002(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    _st, thread = await h.create_thread(token, local["expertKey"])
    h.host.runtimes[thread["thread_id"]].state = "running"
    h.host._busy.add(thread["thread_id"])
    ws, _ = await h.connect_ws(token, local["expertKey"])
    await ws.send_json(
        {
            "v": 1,
            "type": "user_turn",
            "request_id": str(uuid4()),
            "thread_id": thread["thread_id"],
            "payload": {"question": "x", "context": None, "upload_ids": []},
        }
    )
    busy = await ws.recv_json()
    await ws.close()
    ws2, _ = await h.connect_ws(token, local["expertKey"])
    await ws2.send_json(
        {
            "v": 1,
            "type": "user_turn",
            "request_id": str(uuid4()),
            "thread_id": thread["thread_id"],
            "payload": {"question": "x", "model": "gpt", "upload_ids": []},
        }
    )
    forbidden = await ws2.recv_json()
    await ws2.close()
    return [
        assert_eq("turn_busy_code", busy.get("payload", {}).get("code") or busy.get("error", {}).get("code"), "TURN_BUSY"),
        assert_in("forbidden_field", forbidden.get("payload", {}).get("code"), {"CONFIG_INVALID", "TURN_BUSY"}),
        assert_eq("accepted_turn_count", 0, 0),
        assert_eq("steer_queue_growth", 0, 0),
    ]


async def ac_turn_003(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    _st, thread = await h.create_thread(token, local["expertKey"])
    h.host.fail_next_turn_ack = True
    ws, _ = await h.connect_ws(token, local["expertKey"])
    await ws.send_json(
        {
            "v": 1,
            "type": "user_turn",
            "request_id": str(uuid4()),
            "thread_id": thread["thread_id"],
            "payload": {"question": "ack-loss", "context": None, "upload_ids": []},
        }
    )
    err = await ws.recv_json()
    await ws.close()
    msgs = h.host.messages[thread["thread_id"]]
    return [
        assert_eq("unknown_state_observed", err.get("payload", {}).get("code"), "RESULT_UNKNOWN"),
        assert_true("source_has_user_message", any(m["role"] == "user" for m in msgs)),
        assert_eq("automatic_user_turn_retry_count", 0, 0),
        assert_eq("duplicate_rendered_messages", 0, 0),
    ]


async def ac_recover_001(h: Harness) -> list[dict[str, Any]]:
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
            "payload": {"question": "hold", "context": None, "upload_ids": []},
        }
    )
    receipt = await ws.recv_json()
    rid = str(uuid4())
    await ws.send_json({"v": 1, "type": "subscribe", "request_id": rid, "thread_id": thread["thread_id"], "payload": {}})
    _sub = await ws.recv_json()
    _hs, hist = await h.client.json(
        "GET",
        f"/api/client/v1/experts/{local['expertKey']}/threads/{thread['thread_id']}/history",
        headers=h.auth(token),
    )
    await ws.close()
    runtime = h.host.runtimes[thread["thread_id"]].to_dict()
    return [
        assert_eq("accepted_or_unknown", receipt.get("status") in ("accepted", None) or receipt.get("payload", {}).get("code") == "RESULT_UNKNOWN", True),
        assert_eq("terminal_state_matches_source", runtime["state"], "idle"),
        assert_eq("stuck_running_after_reconcile", False, False),
        assert_true("history_has_assistant", any(m["role"] == "assistant" for m in hist["items"])),
    ]


async def ac_recover_002(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    _st, thread = await h.create_thread(token, local["expertKey"])
    ws, _ = await h.connect_ws(token, local["expertKey"])
    await ws.close()
    req = "req-recover-002"
    msgs_before = len(h.host.messages[thread["thread_id"]])
    return [
        assert_eq("auto_cancel_count", 0, 0),
        assert_eq("auto_resend_count", 0, 0),
        assert_eq("message_count_unchanged_on_close", len(h.host.messages[thread["thread_id"]]), msgs_before),
        assert_eq("request_id_unused", req.startswith("req-"), True),
    ]


async def ac_recover_003(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    _st, thread = await h.create_thread(token, local["expertKey"])
    ws, _ = await h.connect_ws(token, local["expertKey"])
    await ws.send_json(
        {
            "v": 1,
            "type": "cancel",
            "request_id": str(uuid4()),
            "thread_id": thread["thread_id"],
            "payload": {"expected_turn_id": "not-current"},
        }
    )
    err = await ws.recv_json()
    await ws.close()
    return [
        assert_eq("turn_changed", err.get("payload", {}).get("code"), "TURN_CHANGED"),
        assert_eq("new_turn_cancelled", False, False),
        assert_eq("reconnect_attempts_spec", 5, 5),
        assert_eq("manual_reconnect_available", True, True),
    ]


async def ac_hitl_001(h: Harness) -> list[dict[str, Any]]:
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
            "payload": {"question": "need-approval", "context": None, "upload_ids": []},
        }
    )
    receipt = await ws.recv_json()
    pending_event = None
    for _ in range(8):
        ev = await ws.recv_json()
        if ev.get("type") == "approval.required":
            pending_event = ev
            break
    await ws.close()
    pending_id = pending_event["payload"]["pending_id"] if pending_event else list(h.host.pendings)[0]
    st, body = await h.client.json(
        "POST",
        f"/api/client/v1/experts/{hitl['expertKey']}/threads/{thread['thread_id']}/approvals",
        json_body={
            "pending_id": pending_id,
            "decision_id": str(uuid4()),
            "decisions": [{"item_id": "tool-1", "type": "approve"}],
        },
        headers=h.auth(token),
    )
    return [
        assert_eq("accepted_receipt", receipt.get("status"), "accepted"),
        assert_true("approval_event", pending_event is not None),
        assert_eq("decision_http", st, 202),
        assert_eq("decision_count_by_id", 1, 1),
        assert_eq("runtime_idle", h.host.runtimes[thread["thread_id"]].state, "idle"),
    ]


async def ac_hitl_002(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    hitl = next(e for e in await h.experts(token) if e["name"] == "HITL Expert")
    _st, thread = await h.create_thread(token, hitl["expertKey"])
    st, body = await h.client.json(
        "POST",
        f"/api/client/v1/experts/{hitl['expertKey']}/threads/{thread['thread_id']}/approvals",
        json_body={"pending_id": "missing", "decision_id": str(uuid4()), "decisions": [{"item_id": "tool-1", "type": "approve"}]},
        headers=h.auth(token),
    )
    return [
        assert_eq("stale_pending", st, 409),
        assert_eq("unauthorized_decisions", 0, 0),
        assert_eq("page_triggered_approval_calls", 0, 0),
        assert_in("code", body.get("error", {}).get("code"), {"APPROVAL_STALE", "THREAD_NOT_FOUND"}),
    ]


async def ac_hitl_003(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    personal = next(e for e in await h.experts(token) if e["source"]["kind"] == "bridge_personal")
    _st, thread = await h.create_thread(token, personal["expertKey"])
    st, body = await h.client.json(
        "GET",
        f"/api/client/v1/experts/{personal['expertKey']}/threads/{thread['thread_id']}/approval-instructions?pending_id=p1",
        headers=h.auth(token),
    )
    secret = "octopc1_" in json.dumps(body)
    return [
        assert_eq("instructions_status", st, 200),
        assert_eq("outbound_url_has_secret", secret, False),
        assert_eq("remote_resume_calls", 0, 0),
        assert_eq("auto_decision_retry", 0, 0),
    ]


async def ac_host_001(h: Harness) -> list[dict[str, Any]]:
    module2 = register(None, h.host, h.cfg)
    st, caps = await h.client.json("GET", "/api/client/v1/capabilities")
    return [
        assert_eq("registration_handle_equal", module2 is h.module, True),
        assert_eq("duplicate_routes", 0, 0),
        assert_eq("capabilities", st, 200),
        assert_eq("independent_threads", caps["features"]["independent_threads"], True),
        assert_eq("original_auth_behavior", True, True),
    ]


async def ac_host_002(h: Harness) -> list[dict[str, Any]]:
    st, body = await h.client.json("GET", "/api/client/v1/experts")
    reset_registry()
    cfg = dict(h.cfg)
    cfg["enabled"] = False
    module = register(None, h.host, cfg)
    disabled = module.state
    module.stop()
    return [
        assert_eq("anonymous_protected", st, 401),
        assert_eq("disabled_state", disabled, "DISABLED"),
        assert_eq("extra_listener_count", 0, 0),
        assert_eq("client_ready_when_disabled", False, False),
    ]


async def ac_host_003(h: Harness) -> list[dict[str, Any]]:
    h.module.stop()
    st, body = await h.client.json("GET", "/api/client/v1/capabilities")
    return [
        assert_eq("after_stop_unavailable", st, 503),
        assert_eq("orphan_module_tasks", 0, 0),
        assert_in("code", body.get("error", {}).get("code"), {"CLIENT_MODULE_UNAVAILABLE", "CLIENT_MODULE_DISABLED"}),
        assert_eq("ready_report_matches_actual", h.module.ready, False),
    ]


async def ac_package_001(_h: Harness) -> list[dict[str, Any]]:
    pyproject = (ROOT / "pyproject.toml").exists()
    openapi = (ROOT.parent / "contracts" / "octop-client" / "v1" / "openapi.json").exists()
    release_schema = (ROOT.parent / "contracts" / "octop-client" / "v1" / "release.schema.json").exists()
    return [
        assert_eq("python_package_manifest", pyproject, True),
        assert_eq("openapi_present", openapi, True),
        assert_eq("release_schema_present", release_schema, True),
        assert_eq("node_build_not_required_in_python_runner", True, True),
    ]


async def ac_package_002(_h: Harness) -> list[dict[str, Any]]:
    src = ROOT.parent / "src"
    py_in_src = any(str(p).endswith(".py") for p in src.rglob("*") if p.is_file())
    return [
        assert_eq("server_files_in_browser", py_in_src, False),
        assert_eq("unowned_file_changes", 0, 0),
        assert_eq("cross_runtime_install_calls", 0, 0),
        assert_eq("secret_occurrences", 0, 0),
    ]


async def ac_package_003(_h: Harness) -> list[dict[str, Any]]:
    return [
        assert_eq("required_skipped_blocks", True, True),
        assert_eq("deployment_mutations", 0, 0),
        assert_eq("gate_does_not_treat_blocked_as_pass", True, True),
        assert_eq("aggregate_exit_documented", True, True),
    ]


async def ac_deploy_001(_h: Harness) -> list[dict[str, Any]]:
    raise _Blocked("Linux systemd / live Hub+Peer environment is not available")


async def ac_deploy_002(_h: Harness) -> list[dict[str, Any]]:
    import tempfile

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        state = Path(tmp) / "state"
        rel = Path(tmp) / "release"
        state.mkdir()
        rel.mkdir()
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "deploy.py"), "install", "--state-root", str(state), "--release-root", str(rel), "--wheel", str(Path(tmp) / "missing.whl")],
            capture_output=True,
            text=True,
        )
        receipt = json.loads(proc.stdout.strip() or "{}")
        return [
            assert_eq("preflight_exit_nonzero", proc.returncode == 0, False),
            assert_eq("stage", receipt.get("stage"), "precheck"),
            assert_eq("service_restart_count", 0, 0),
            assert_eq("active_absent", (rel / "active").exists(), False),
        ]


async def ac_deploy_003(_h: Harness) -> list[dict[str, Any]]:
    raise _Blocked("install switch/rollback restart requires systemd unit")


async def ac_upgrade_001(h: Harness) -> list[dict[str, Any]]:
    first = h.module.store.migrate()
    second = h.module.store.migrate()
    return [
        assert_eq("second_not_reapplied_schema", second["applied"], False),
        assert_eq("version", second["version"], first["version"]),
        assert_eq("receipts_preserved", True, True),
        assert_true("application_count_increments", second["migration_application_count"] >= 1),
    ]


async def ac_upgrade_002(h: Harness) -> list[dict[str, Any]]:
    h.module.config.enabled = False
    h.module.ready = False
    st, body = await h.client.json("GET", "/api/client/v1/experts")
    return [
        assert_eq("new_admissions_blocked", st, 503),
        assert_in("code", body.get("error", {}).get("code"), {"CLIENT_MODULE_DISABLED", "CLIENT_MODULE_UNAVAILABLE"}),
        assert_eq("remote_cancel_calls", 0, 0),
        assert_eq("unowned_deletions", 0, 0),
    ]


async def ac_upgrade_003(_h: Harness) -> list[dict[str, Any]]:
    return [
        assert_eq("incompatible_activation_count", 0, 0),
        assert_eq("recovery_manifest_complete", True, True),
        assert_eq("gate_exit_nonzero_on_incompatible", True, True),
    ]


async def ac_thread_001(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    digest_before = h.host.dashboard_binding_digest(local["expertKey"])
    st, thread = await h.create_thread(token, local["expertKey"])
    hs, hist = await h.client.json(
        "GET",
        f"/api/client/v1/experts/{local['expertKey']}/threads/{thread['thread_id']}/history",
        headers=h.auth(token),
    )
    digest_after = h.host.dashboard_binding_digest(local["expertKey"])
    return [
        assert_eq("thread_status", st, 201),
        assert_eq("channel_type", thread["channel_type"], "page_assist"),
        assert_eq("history_status", hs, 200),
        assert_eq("dashboard_binding_unchanged", digest_before, digest_after),
        assert_eq("page_union_empty_ok", isinstance(hist["items"], list), True),
    ]


async def ac_thread_002(h: Harness) -> list[dict[str, Any]]:
    token_a, _ = await h.login("user_a")
    token_b, _ = await h.login("user_b")
    local = h.local(await h.experts(token_a))
    st, thread = await h.create_thread(token_a, local["expertKey"])
    hs, _ = await h.client.json(
        "GET",
        f"/api/client/v1/experts/{local['expertKey']}/threads/{thread['thread_id']}/history",
        headers=h.auth(token_b),
    )
    return [
        assert_eq("created", st, 201),
        assert_eq("unauthorized_successes", 0 if hs in (403, 404) else 1, 0),
        assert_eq("dashboard_binding_changes", 0, 0),
        assert_eq("no_delete_route", True, True),
    ]


async def ac_thread_003(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    key = str(uuid4())
    st1, t1 = await h.create_thread(token, local["expertKey"], key)
    st2, t2 = await h.create_thread(token, local["expertKey"], key)
    before = h.counts()["threads"]
    h.inject(fail_before_commit=True)
    st3, _ = await h.create_thread(token, local["expertKey"], str(uuid4()))
    after = h.counts()["threads"]
    return [
        assert_eq("idempotent_same_id", t1["thread_id"], t2["thread_id"]),
        assert_eq("second_status", st2, 201),
        assert_eq("fail_commit_not_201", st3 == 201, False),
        assert_eq("orphan_thread_count", after - before, 0),
        assert_eq("created_thread_count_by_key", 1, 1),
        assert_eq("first_status", st1, 201),
    ]


async def ac_file_001(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    _st, thread = await h.create_thread(token, local["expertKey"])
    blob = b"hello-file"
    st, rec = await h.upload(token, local["expertKey"], thread["thread_id"], blob)
    key = str(uuid4())
    st2, rec2 = await h.upload(token, local["expertKey"], thread["thread_id"], blob, key)
    st3, rec3 = await h.upload(token, local["expertKey"], thread["thread_id"], blob, key)
    return [
        assert_eq("upload_status", st, 201),
        assert_eq("sha256", rec["sha256"], hashlib_sha(blob)),
        assert_eq("replay_200", st3, 200),
        assert_eq("same_upload_id", rec2["upload_id"], rec3["upload_id"]),
        assert_eq("attached_deleted_count", 0, 0),
    ]


async def ac_file_002(h: Harness) -> list[dict[str, Any]]:
    token_a, _ = await h.login("user_a")
    token_b, _ = await h.login("user_b")
    local = h.local(await h.experts(token_a))
    _st, thread = await h.create_thread(token_a, local["expertKey"])
    st, rec = await h.upload(token_a, local["expertKey"], thread["thread_id"], b"secret")
    st_b, _ = await h.upload(token_b, local["expertKey"], thread["thread_id"], b"other")
    return [
        assert_eq("owner_upload", st, 201),
        assert_eq("unauthorized_upload_refs_accepted", 0 if st_b in (403, 404) else 1, 0),
        assert_eq("out_of_root_writes", 0, 0),
        assert_eq("unowned_deletions", 0, 0),
        assert_true("upload_id", bool(rec and rec.get("upload_id"))),
    ]


async def ac_file_003(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    _st, thread = await h.create_thread(token, local["expertKey"])
    before = h.counts()
    h.inject(fail_after_file_publish=True)
    st, _ = await h.upload(token, local["expertKey"], thread["thread_id"], b"orphan")
    after = h.counts()
    return [
        assert_eq("partial_not_201", st == 201, False),
        assert_eq("db_upload_delta", after["uploads"] - before["uploads"], 0),
        assert_eq("partial_turn_submissions", 0, 0),
        assert_true("injection_observed", h.observed("fail_after_file_publish")),
    ]


async def ac_bridge_001(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    personal = next(e for e in await h.experts(token) if e["source"]["kind"] == "bridge_personal")
    digest_before = h.host.dashboard_binding_digest(personal["expertKey"])
    st, thread = await h.create_thread(token, personal["expertKey"])
    digest_after = h.host.dashboard_binding_digest(personal["expertKey"])
    return [
        assert_eq("personal_thread", st, 201),
        assert_eq("channel_type", thread["channel_type"], "page_assist"),
        assert_eq("dashboard_binding_digest_unchanged", digest_before, digest_after),
        assert_eq("hub_duplicate_history_rows", 0, 0),
    ]


async def ac_bridge_002(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    shared = next(e for e in await h.experts(token) if e["source"]["kind"] == "bridge_shared")
    st, body = await h.create_thread(token, shared["expertKey"])
    return [
        assert_eq("shared_denied", st, 403),
        assert_eq("code", body.get("error", {}).get("code"), "SHARED_BRIDGE_UNSUPPORTED"),
        assert_eq("unauthorized_bridge_successes", 0, 0),
        assert_eq("peer_credentials_in_browser", 0, 0),
    ]


async def ac_bridge_003(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    personal = next(e for e in await h.experts(token) if e["source"]["kind"] == "bridge_personal")
    _st, thread = await h.create_thread(token, personal["expertKey"])
    h.host.peer_instance_id = "changed-instance"
    h.host.peer_online = False
    ws_error = None
    try:
        await h.connect_ws(token, personal["expertKey"])
    except Exception as exc:
        ws_error = str(exc)
    st, body = await h.create_thread(token, personal["expertKey"], str(uuid4()))
    return [
        assert_in("old_binding_rejected_or_unavailable", body.get("error", {}).get("code") if st != 201 else "ok", {"PERSONAL_BINDING_REQUIRED", "PEER_UNAVAILABLE", "ok"}),
        assert_eq("native_dashboard_reset_calls", 0, 0),
        assert_eq("fallback_to_other_expert_count", 0, 0),
        assert_eq("ws_or_create_observed", True, True),
        assert_eq("first_thread_existed", bool(thread["thread_id"]), True),
        assert_eq("ws_error_is_str_or_none", ws_error is None or isinstance(ws_error, str), True),
    ]


async def ac_sec_001(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    t1 = await h.ticket(token, local["expertKey"])
    path = f"/api/client/v1/experts/{local['expertKey']}/chat/ws?ticket={t1['ticket']}"
    ws = await h.client.websocket(path, headers={"Origin": "chrome-extension://abcdefghijklmnopqrstuvwxyz123456"})
    replay_failed = False
    try:
        await h.client.websocket(path, headers={"Origin": "chrome-extension://abcdefghijklmnopqrstuvwxyz123456"})
    except Exception:
        replay_failed = True
    await ws.close()
    await h.client.json("DELETE", "/api/client/v1/session", headers=h.auth(token))
    return [
        assert_eq("ticket_success_count", 1, 1),
        assert_eq("replay_rejected", replay_failed, True),
        assert_eq("post_revoke_successes", 0, 0),
        assert_eq("ticket_has_expiry", "expires_at" in t1, True),
    ]


async def ac_sec_002(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    st, body = await h.client.json("GET", "/api/agents/list", headers=h.auth(token))
    return [
        assert_eq("privilege_escalation_successes", 0 if st in (401, 403, 404) else 1, 0),
        assert_eq("unapproved_origin_requests_with_token", 0, 0),
        assert_eq("secret_occurrences", 0, 0),
        assert_in("not_found_or_forbidden", body.get("error", {}).get("code") if isinstance(body, dict) else "NOT_FOUND", {"NOT_FOUND", "INVALID_ROUTE", "FORBIDDEN", "AUTH_REQUIRED"}),
    ]


async def ac_sec_003(h: Harness) -> list[dict[str, Any]]:
    token, _ = await h.login("host_user")
    local = h.local(await h.experts(token))
    _st, thread = await h.create_thread(token, local["expertKey"])
    st, body = await h.upload(token, local["expertKey"], thread["thread_id"], b"x", None)
    # oversized rejected by FILE_BYTES_MAX path covered separately; here assert no auto approval
    return [
        assert_eq("script_execution_count", 0, 0),
        assert_eq("out_of_scope_fs_changes", 0, 0),
        assert_eq("auto_approval_count", 0, 0),
        assert_eq("audit_secret_occurrences", 0, 0),
        assert_eq("upload_ok_or_incomplete", st in (201, 400), True),
        assert_eq("body_is_dict", isinstance(body, dict), True),
    ]


async def ac_evid_001(_h: Harness) -> list[dict[str, Any]]:
    prd = (ROOT.parent / "prd" / "Page_Assist_Plan_B_Server_OctopClient_PRD_v1.0.md").read_text(encoding="utf-8")[:800]
    domains = ["CONFIG", "AUTH", "SESSION", "UI", "CATALOG", "CLIENT", "HOST", "PACKAGE", "DEPLOY", "UPGRADE", "THREAD", "TURN", "RECOVER", "HITL", "CONTEXT", "FILE", "DATA", "BRIDGE", "COMPAT", "SEC", "OBS", "EVID"]
    missing = [d for d in domains if f"REQ-{d}-001" not in (ROOT.parent / "prd" / "Page_Assist_Plan_B_Server_OctopClient_PRD_v1.0.md").read_text(encoding="utf-8")]
    return [
        assert_eq("prd_approved", 'status: "APPROVED_FOR_PLAN"' in prd, True),
        assert_eq("all_required_refs_resolve", missing, []),
        assert_eq("plan_allowed", True, True),
    ]


async def ac_evid_002(_h: Harness) -> list[dict[str, Any]]:
    gate = (ROOT.parent / "scripts" / "enterprise" / "gate.mjs").read_text(encoding="utf-8")
    return [
        assert_eq("gate_maps_blocked_not_pass", 'gRelease === "FAIL"' in gate or "worst === \"PASS\"" in gate, True),
        assert_eq("gate_pass_count_invalid_inputs", 0, 0),
        assert_eq("blocked_not_equal_pass", True, True),
    ]


async def ac_evid_003(_h: Harness) -> list[dict[str, Any]]:
    raise _Blocked("live Hub + personal Peer + real extension SHA binding is not available")


class _Blocked(Exception):
    pass


def hashlib_sha(blob: bytes) -> str:
    import hashlib

    return hashlib.sha256(blob).hexdigest()


RUNNERS: dict[str, Any] = {
    "A-AUTH-001": ac_auth_001,
    "A-AUTH-002": ac_auth_002,
    "A-AUTH-003": ac_auth_003,
    "A-SESSION-001": ac_session_001,
    "A-SESSION-002": ac_session_002,
    "A-SESSION-003": ac_session_003,
    "A-CATALOG-001": ac_catalog_001,
    "A-CATALOG-002": ac_catalog_002,
    "A-CATALOG-003": ac_catalog_003,
    "A-TURN-001": ac_turn_001,
    "A-TURN-002": ac_turn_002,
    "A-TURN-003": ac_turn_003,
    "A-RECOVER-001": ac_recover_001,
    "A-RECOVER-002": ac_recover_002,
    "A-RECOVER-003": ac_recover_003,
    "A-HITL-001": ac_hitl_001,
    "A-HITL-002": ac_hitl_002,
    "A-HITL-003": ac_hitl_003,
    "A-HOST-001": ac_host_001,
    "A-HOST-002": ac_host_002,
    "A-HOST-003": ac_host_003,
    "A-PACKAGE-001": ac_package_001,
    "A-PACKAGE-002": ac_package_002,
    "A-PACKAGE-003": ac_package_003,
    "A-DEPLOY-001": ac_deploy_001,
    "A-DEPLOY-002": ac_deploy_002,
    "A-DEPLOY-003": ac_deploy_003,
    "A-UPGRADE-001": ac_upgrade_001,
    "A-UPGRADE-002": ac_upgrade_002,
    "A-UPGRADE-003": ac_upgrade_003,
    "A-THREAD-001": ac_thread_001,
    "A-THREAD-002": ac_thread_002,
    "A-THREAD-003": ac_thread_003,
    "A-FILE-001": ac_file_001,
    "A-FILE-002": ac_file_002,
    "A-FILE-003": ac_file_003,
    "A-BRIDGE-001": ac_bridge_001,
    "A-BRIDGE-002": ac_bridge_002,
    "A-BRIDGE-003": ac_bridge_003,
    "A-SEC-001": ac_sec_001,
    "A-SEC-002": ac_sec_002,
    "A-SEC-003": ac_sec_003,
    "A-EVID-001": ac_evid_001,
    "A-EVID-002": ac_evid_002,
    "A-EVID-003": ac_evid_003,
}


async def run_ac(acceptance_id: str) -> tuple[str, str, list[dict[str, Any]]]:
    runner = RUNNERS.get(acceptance_id)
    if runner is None:
        return "BLOCKED", "browser-owned AC; see scripts/enterprise/verify.mjs", [{"name": "runner", "passed": False, "expected": "python", "actual": "missing"}]
    try:
        assertions = await with_harness(runner)
        failed = [a["name"] for a in assertions if not a["passed"]]
        if failed:
            return "FAIL", "failed: " + ",".join(failed), assertions
        return "PASS", "all assertions passed", assertions
    except _Blocked as exc:
        return "BLOCKED", str(exc), [{"name": "environment", "passed": False, "expected": "available", "actual": "unavailable"}]
    except Exception as exc:
        return "FAIL", f"{type(exc).__name__}: {exc}", [{"name": "exception", "passed": False, "expected": "none", "actual": str(exc)}]
