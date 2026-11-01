from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlencode
from uuid import uuid4

from page_assist_octop_client.auth.tokens import hash_secret, new_token, pkce_challenge, token_hash
from page_assist_octop_client.constants import (
    ALLOWED_MEDIA,
    ALLOWED_SCOPES,
    API_PREFIX,
    AUTH_CODE_TTL_SECONDS,
    AUTH_TRANSACTION_TTL_SECONDS,
    CORE_FEATURES,
    CURSOR_TTL_SECONDS,
    FILE_BYTES_MAX,
    PAGE_SIZE,
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    RECEIPT_TTL_SECONDS,
    SESSION_TTL_SECONDS,
    WS_TICKET_TTL_SECONDS,
)
from page_assist_octop_client.cursors import issue_cursor, read_cursor
from page_assist_octop_client.errors import ApiError
from page_assist_octop_client.jcs import account_partition, sha256_hex, sha256_jcs
from page_assist_octop_client.timeutil import later, parse_rfc3339, rfc3339, utcnow
from page_assist_octop_client import __version__


def dispatch(module: Any, name: str, method: str, params: dict[str, str], query: dict[str, str], headers: dict[str, str], body: bytes, scope: dict[str, Any]) -> tuple[int, Any, list[tuple[bytes, bytes]] | None]:
    table = {
        "capabilities": capabilities,
        "auth_transactions": auth_transactions,
        "auth_exchange": auth_exchange,
        "get_session": get_session,
        "delete_session": delete_session,
        "list_experts": list_experts,
        "list_threads": list_threads,
        "create_thread": create_thread,
        "get_history": get_history,
        "upload": upload,
        "ws_tickets": ws_tickets,
        "approvals": approvals,
        "approval_instructions": approval_instructions,
    }
    handler = table.get(name)
    if handler is None:
        raise ApiError("INVALID_ROUTE", "unknown handler", status=404)
    return handler(module, params, query, headers, body, scope)


def _json(body: bytes) -> dict[str, Any]:
    if not body:
        return {}
    try:
        data = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ApiError("CONFIG_INVALID", "invalid json", status=400) from exc
    if not isinstance(data, dict):
        raise ApiError("CONFIG_INVALID", "json object required", status=400)
    return data


def _origin(headers: dict[str, str], scope: dict[str, Any]) -> str:
    origin = headers.get("origin") or headers.get("x-extension-origin") or ""
    return origin


def capabilities(module: Any, params: dict[str, str], query: dict[str, str], headers: dict[str, str], body: bytes, scope: dict[str, Any]) -> tuple[int, Any, None]:
    if not module.config.enabled or not module.ready:
        raise ApiError("CLIENT_MODULE_UNAVAILABLE", "module not ready", status=503)
    host = module.host
    if not host.is_ready() or not host.is_setup_complete():
        raise ApiError("CLIENT_MODULE_UNAVAILABLE", "host not ready", status=503)
    payload = {
        "protocol": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "build": {
            "module_version": __version__,
            "host_api_version": 1,
            "host_build_id": host.get_host_build_id(),
            "ready": True,
        },
        "instance_id": host.get_instance_id(),
        "auth": {"mode": "hosted_pkce", "session_ttl_seconds": SESSION_TTL_SECONDS},
        "features": {name: True for name in CORE_FEATURES},
        "limits": {
            "question_utf8_bytes": 32768,
            "context_utf8_bytes": 65536,
            "turn_json_bytes": 131072,
            "file_bytes": FILE_BYTES_MAX,
            "files_per_turn": 5,
            "files_total_bytes": 20971520,
        },
    }
    return 200, payload, None


def auth_transactions(module: Any, params: dict[str, str], query: dict[str, str], headers: dict[str, str], body: bytes, scope: dict[str, Any]) -> tuple[int, Any, None]:
    data = _json(body)
    required = {"client_id", "redirect_uri", "state", "code_challenge", "method"}
    extra = set(data) - required
    missing = required - set(data)
    if missing or extra:
        raise ApiError("CONFIG_INVALID", "invalid auth transaction fields", status=400)
    if data["method"] != "S256":
        raise ApiError("AUTH_STATE_MISMATCH", "PKCE method must be S256", status=400)
    client = module.config.client_by_id(data["client_id"])
    if client is None or data["redirect_uri"] != client.redirect_uri:
        raise ApiError("AUTH_STATE_MISMATCH", "redirect_uri is not registered", status=400)
    now = rfc3339()
    expires = later(AUTH_TRANSACTION_TTL_SECONDS)
    tx_id = str(uuid4())
    module.store.insert_transaction(
        {
            "transaction_id": tx_id,
            "client_id": data["client_id"],
            "redirect_uri": data["redirect_uri"],
            "state": data["state"],
            "code_challenge": data["code_challenge"],
            "method": "S256",
            "created_at": now,
            "expires_at": expires,
        }
    )
    login_url = f"{module.config.public_origin}/__fixture__/login?" + urlencode(
        {"transaction_id": tx_id, "state": data["state"]}
    )
    if not module.config.fixture_mode:
        login_url = f"{module.config.public_origin}/login?" + urlencode(
            {"transaction_id": tx_id, "state": data["state"], "client_id": data["client_id"]}
        )
    return 201, {"authorization_url": login_url, "expires_at": expires}, None


def auth_exchange(module: Any, params: dict[str, str], query: dict[str, str], headers: dict[str, str], body: bytes, scope: dict[str, Any]) -> tuple[int, Any, None]:
    data = _json(body)
    required = {"client_id", "redirect_uri", "code", "code_verifier"}
    if set(data) != required:
        raise ApiError("CONFIG_INVALID", "invalid exchange fields", status=400)
    code_hash = hash_secret(data["code"])
    row = module.store.get_code(code_hash)
    if row is None:
        raise ApiError("AUTH_CODE_INVALID", "code invalid", status=400)
    now_dt = utcnow()
    if row["consumed_at"] is not None or parse_rfc3339(row["expires_at"]) < now_dt:
        raise ApiError("AUTH_CODE_INVALID", "code expired or reused", status=400)
    if row["client_id"] != data["client_id"] or row["redirect_uri"] != data["redirect_uri"]:
        raise ApiError("AUTH_CODE_INVALID", "code client mismatch", status=400)
    tx = module.store.get_transaction(row["transaction_id"])
    if tx is None:
        raise ApiError("AUTH_CODE_INVALID", "transaction missing", status=400)
    if pkce_challenge(data["code_verifier"]) != tx["code_challenge"]:
        raise ApiError("AUTH_STATE_MISMATCH", "pkce verifier mismatch", status=400)
    with module.store.txn():
        consumed = module.store.consume_code(code_hash, rfc3339())
        if consumed != 1:
            raise ApiError("AUTH_CODE_INVALID", "code already consumed", status=400)
        module.store.consume_transaction(row["transaction_id"], rfc3339())
        user = module.host.lookup_user(row["subject"])
        if user is None or not user.enabled:
            raise ApiError("AUTH_CODE_INVALID", "user disabled", status=400)
        token = new_token()
        sid = str(uuid4())
        session = {
            "sid": sid,
            "instance_id": module.host.get_instance_id(),
            "tenant_id": user.tenant_id,
            "subject": user.id,
            "display_name": user.display_name,
            "expires_at": later(SESSION_TTL_SECONDS),
            "client_id": data["client_id"],
            "scopes": list(ALLOWED_SCOPES),
        }
        module.store.insert_session(
            {
                **session,
                "token_sha256": token_hash(token),
                "scopes": json.dumps(session["scopes"]),
                "created_at": rfc3339(),
            }
        )
    return 200, {"access_token": token, "token_type": "Bearer", "session": session}, None


def _require_session(module: Any, headers: dict[str, str]) -> dict[str, Any]:
    auth = headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise ApiError("AUTH_REQUIRED", "missing bearer token", status=401)
    token = auth[7:].strip()
    if token.startswith("eyJ") or not token.startswith("octopc1_"):
        raise ApiError("AUTH_REQUIRED", "native jwt is not a client token", status=401)
    row = module.store.get_session_by_token_hash(token_hash(token))
    if row is None:
        raise ApiError("SESSION_REVOKED", "unknown session", status=401)
    if row["revoked_at"] is not None:
        raise ApiError("SESSION_REVOKED", "session revoked", status=401)
    if parse_rfc3339(row["expires_at"]) < utcnow():
        raise ApiError("SESSION_EXPIRED", "session expired", status=401)
    user = module.host.lookup_user(row["subject"])
    if user is None or not user.enabled:
        raise ApiError("SESSION_REVOKED", "user disabled", status=401)
    row = dict(row)
    row["scopes"] = json.loads(row["scopes"])
    row["_token"] = token
    return row


def _public_session(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "sid": row["sid"],
        "instance_id": row["instance_id"],
        "tenant_id": row["tenant_id"],
        "subject": row["subject"],
        "display_name": row["display_name"],
        "expires_at": row["expires_at"],
        "client_id": row["client_id"],
        "scopes": row["scopes"],
    }


def get_session(module: Any, params: dict[str, str], query: dict[str, str], headers: dict[str, str], body: bytes, scope: dict[str, Any]) -> tuple[int, Any, None]:
    row = _require_session(module, headers)
    return 200, _public_session(row), None


def delete_session(module: Any, params: dict[str, str], query: dict[str, str], headers: dict[str, str], body: bytes, scope: dict[str, Any]) -> tuple[int, Any, None]:
    try:
        row = _require_session(module, headers)
        module.store.revoke_session(row["sid"], rfc3339())
        module.close_connections(row["sid"])
    except ApiError as err:
        if err.code in ("SESSION_REVOKED", "SESSION_EXPIRED", "AUTH_REQUIRED"):
            return 204, None, None
        raise
    return 204, None, None


def _catalog_revision(items: list[dict[str, Any]]) -> str:
    return sha256_hex(json.dumps(sorted(item["expertKey"] for item in items)).encode("utf-8"))


def _signed_cursor(module: Any, claims: dict[str, Any]) -> str:
    snapshot_id = str(uuid4())
    now = rfc3339()
    module.store.insert_cursor_snapshot(
        {
            "snapshot_id": snapshot_id,
            "scope": claims["scope"],
            "sid": claims["sid"],
            "revision": claims["revision"],
            "created_at": now,
            "expires_at": later(CURSOR_TTL_SECONDS),
        }
    )
    return issue_cursor(module.cursor_key, {**claims, "snapshot_id": snapshot_id})


def _verify_cursor(module: Any, cursor: str, scope: str, sid: str, filter_key: str, revision: str) -> int:
    claims = read_cursor(module.cursor_key, cursor)
    if claims is None or claims.get("scope") != scope:
        raise ApiError("CURSOR_STALE", "invalid cursor", status=409)
    if claims.get("sid") != sid or claims.get("filter") != filter_key:
        raise ApiError("CURSOR_STALE", "cursor does not match session or filter", status=409)
    if claims.get("revision") != revision:
        raise ApiError("CURSOR_STALE", "catalog revision changed", status=409)
    snapshot = module.store.get_cursor_snapshot(str(claims.get("snapshot_id", "")))
    if snapshot is None or parse_rfc3339(snapshot["expires_at"]) < utcnow():
        raise ApiError("CURSOR_STALE", "cursor expired", status=409)
    return int(claims["offset"])


def _paginate_signed(
    module: Any,
    session: dict[str, Any],
    scope: str,
    filter_key: str,
    items: list[Any],
    cursor: str | None,
    revision: str,
    size: int = PAGE_SIZE,
) -> tuple[list[Any], str | None]:
    if cursor:
        start = _verify_cursor(module, cursor, scope, session["sid"], filter_key, revision)
    else:
        start = 0
    if start > len(items):
        raise ApiError("CURSOR_STALE", "cursor out of range", status=409)
    page = items[start : start + size]
    nxt = None
    if start + size < len(items):
        nxt = _signed_cursor(
            module,
            {
                "scope": scope,
                "sid": session["sid"],
                "filter": filter_key,
                "revision": revision,
                "offset": start + size,
            },
        )
    return page, nxt


def list_experts(module: Any, params: dict[str, str], query: dict[str, str], headers: dict[str, str], body: bytes, scope: dict[str, Any]) -> tuple[int, Any, None]:
    session = _require_session(module, headers)
    source = query.get("source", "all")
    if source not in ("all", "local", "remote"):
        raise ApiError("CONFIG_INVALID", "invalid source", status=400)
    q = query.get("q") or ""
    items = module.host.list_experts(session["subject"], source, query.get("q"))
    revision = _catalog_revision(items)
    page, cursor = _paginate_signed(module, session, "catalog", f"{source}|{q}", items, query.get("cursor"), revision)
    for item in page:
        if item["source"]["kind"] == "bridge_shared":
            item["availability"] = "unsupported"
            item["unavailable_reason"] = "SHARED_BRIDGE_UNSUPPORTED"
            item["capabilities"]["create_thread"] = False
            item["capabilities"]["chat"] = False
    return 200, {"items": page, "next_cursor": cursor}, None


def _require_expert(module: Any, session: dict[str, Any], key: str, action: str) -> dict[str, Any]:
    expert = module.host.get_expert(key)
    if expert is None or not module.host.check_acl(session["subject"], key, action):
        raise ApiError("EXPERT_NOT_FOUND", "expert not found", status=404)
    if expert["source"]["kind"] == "bridge_shared":
        raise ApiError("SHARED_BRIDGE_UNSUPPORTED", "shared bridge private chat is not supported", status=403)
    return expert


def list_threads(module: Any, params: dict[str, str], query: dict[str, str], headers: dict[str, str], body: bytes, scope: dict[str, Any]) -> tuple[int, Any, None]:
    session = _require_session(module, headers)
    expert = _require_expert(module, session, params["key"], "read")
    items = module.host.list_threads(session["subject"], params["key"])
    public = [_public_thread(t) for t in items]
    raw = module.host.get_expert_raw(params["key"]) or {}
    generation = raw.get("_generation", 0)
    revision = sha256_hex(
        json.dumps({"g": generation, "t": sorted(t["thread_id"] for t in items)}, sort_keys=True).encode("utf-8")
    )
    partition = account_partition(
        module.config.public_origin,
        session["instance_id"],
        session["tenant_id"],
        session["subject"],
    )
    page, cursor = _paginate_signed(
        module, session, "threads", f"{partition}|{params['key']}", public, query.get("cursor"), revision
    )
    return 200, {"items": page, "next_cursor": cursor}, None


def _public_thread(thread: dict[str, Any]) -> dict[str, Any]:
    return {
        "thread_id": thread["thread_id"],
        "expertKey": thread["expertKey"],
        "channel_type": "page_assist",
        "title": thread.get("title") or "",
        "created_at": thread["created_at"],
        "updated_at": thread["updated_at"],
        "runtime": thread["runtime"],
    }


def create_thread(module: Any, params: dict[str, str], query: dict[str, str], headers: dict[str, str], body: bytes, scope: dict[str, Any]) -> tuple[int, Any, None]:
    session = _require_session(module, headers)
    expert = _require_expert(module, session, params["key"], "create")
    data = _json(body)
    if data:
        raise ApiError("CONFIG_INVALID", "create thread body must be empty object", status=400)
    request_id = headers.get("idempotency-key")
    if not request_id:
        raise ApiError("CONFIG_INVALID", "Idempotency-Key required", status=400)
    partition = account_partition(
        module.config.public_origin,
        session["instance_id"],
        session["tenant_id"],
        session["subject"],
    )
    request_hash = sha256_jcs({"expertKey": params["key"], "body": {}})
    existing = module.store.get_receipt(
        partition, session["instance_id"], session["client_id"], "threads.create", params["key"], request_id
    )
    if existing:
        if existing["request_hash"] != request_hash:
            raise ApiError("IDEMPOTENCY_CONFLICT", "idempotency key reused with different body", status=409)
        return int(existing["status_code"]), json.loads(existing["response_json"]), None
    thread: dict[str, Any] | None = None
    try:
        with module.store.txn():
            if module.host.bridge_kind(params["key"]) == "bridge_personal":
                module.bridge.ensure_personal_binding(session, expert)
            thread = module.host.create_thread(session["subject"], params["key"], request_id)
            module.store.insert_thread_meta(
                {
                    "thread_id": thread["thread_id"],
                    "expert_key": params["key"],
                    "owner_subject": session["subject"],
                    "channel_type": "page_assist",
                    "title": thread.get("title") or "",
                    "created_at": thread["created_at"],
                    "updated_at": thread["updated_at"],
                    "source_kind": expert["source"]["kind"],
                }
            )
            public = _public_thread(thread)
            module.store.save_receipt(
                {
                    "receipt_id": str(uuid4()),
                    "account_partition": partition,
                    "source_instance_id": session["instance_id"],
                    "client_id": session["client_id"],
                    "operation": "threads.create",
                    "resource_identity": params["key"],
                    "request_id": request_id,
                    "request_hash": request_hash,
                    "status_code": 201,
                    "response_json": json.dumps(public, ensure_ascii=False),
                    "created_at": rfc3339(),
                    "expires_at": later(RECEIPT_TTL_SECONDS),
                }
            )
    except Exception:
        if thread is not None and hasattr(module.host, "forget_thread"):
            meta = module.store.get_thread_meta(thread["thread_id"])
            if meta is None:
                module.host.forget_thread(thread["thread_id"])
        raise
    return 201, public, None


def get_history(module: Any, params: dict[str, str], query: dict[str, str], headers: dict[str, str], body: bytes, scope: dict[str, Any]) -> tuple[int, Any, None]:
    session = _require_session(module, headers)
    _require_expert(module, session, params["key"], "read")
    thread = module.host.get_thread(params["id"])
    if thread is None or thread["owner"] != session["subject"] or thread["expertKey"] != params["key"]:
        raise ApiError("THREAD_NOT_FOUND", "thread not found", status=404)
    raw_expert = module.host.get_expert_raw(params["key"]) or {}
    generation = raw_expert.get("_generation", 0)
    partition = account_partition(
        module.config.public_origin,
        session["instance_id"],
        session["tenant_id"],
        session["subject"],
    )
    claims: dict[str, Any] = {
        "scope": "history",
        "subject": session["subject"],
        "partition": partition,
        "expert": params["key"],
        "thread": params["id"],
        "generation": generation,
    }
    raw_cursor = query.get("cursor")
    if raw_cursor:
        saved = read_cursor(module.cursor_key, raw_cursor)
        if saved is None or saved.get("scope") != "history":
            raise ApiError("CURSOR_STALE", "invalid cursor", status=409)
        for key in ("subject", "partition", "expert", "thread"):
            if saved.get(key) != claims[key]:
                raise ApiError("CURSOR_STALE", "cursor does not match source identity", status=409)
        if saved.get("generation") != generation:
            raise ApiError("CURSOR_STALE", "projection generation changed", status=409)
        host_cursor = str(saved.get("offset", "0"))
    else:
        host_cursor = None
    page = module.host.get_history(params["id"], host_cursor)
    next_raw = page.get("next_cursor")
    page["next_cursor"] = None
    if next_raw:
        page["next_cursor"] = issue_cursor(module.cursor_key, {**claims, "offset": next_raw})
    return 200, page, None


def _parse_multipart(headers: dict[str, str], body: bytes) -> dict[str, Any]:
    ctype = headers.get("content-type", "")
    match = re.search(r"boundary=([^;]+)", ctype)
    if not match:
        raise ApiError("UPLOAD_INCOMPLETE", "multipart boundary missing", status=400)
    boundary = match.group(1).strip().strip('"').encode()
    parts = body.split(b"--" + boundary)
    fields: dict[str, Any] = {}
    for part in parts:
        if part in (b"", b"--", b"--\r\n", b"\r\n"):
            continue
        if part.startswith(b"--"):
            continue
        header_blob, _, content = part.partition(b"\r\n\r\n")
        content = content.rstrip(b"\r\n")
        disp = header_blob.decode("utf-8", "replace")
        name_m = re.search(r'name="([^"]+)"', disp)
        if not name_m:
            continue
        name = name_m.group(1)
        filename_m = re.search(r'filename="([^"]+)"', disp)
        type_m = re.search(r"Content-Type:\s*([^\r\n]+)", disp, re.I)
        if filename_m:
            fields[name] = {
                "filename": filename_m.group(1),
                "content_type": (type_m.group(1).strip() if type_m else "application/octet-stream"),
                "data": content,
            }
        else:
            fields[name] = content.decode("utf-8")
    return fields


def upload(module: Any, params: dict[str, str], query: dict[str, str], headers: dict[str, str], body: bytes, scope: dict[str, Any]) -> tuple[int, Any, None]:
    session = _require_session(module, headers)
    _require_expert(module, session, params["key"], "upload")
    thread = module.host.get_thread(params["id"])
    if thread is None or thread["owner"] != session["subject"] or thread["expertKey"] != params["key"]:
        raise ApiError("THREAD_NOT_FOUND", "thread not found", status=404)
    request_id = headers.get("idempotency-key")
    if not request_id:
        raise ApiError("CONFIG_INVALID", "Idempotency-Key required", status=400)
    fields = _parse_multipart(headers, body)
    file_part = fields.get("file")
    sha = fields.get("sha256")
    if not isinstance(file_part, dict) or not sha:
        raise ApiError("UPLOAD_INCOMPLETE", "file and sha256 required", status=400)
    media = file_part["content_type"]
    if media not in ALLOWED_MEDIA:
        raise ApiError("UNSUPPORTED_MEDIA", "media type not allowed", status=415)
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
        raise ApiError("UPLOAD_INCOMPLETE", "sha256 must be 64 lowercase hex chars", status=400)
    if len(file_part["data"]) > FILE_BYTES_MAX:
        raise ApiError("UPLOAD_TOO_LARGE", "file exceeds limit", status=413)
    if sha256_hex(file_part["data"]) != sha:
        raise ApiError("UPLOAD_INCOMPLETE", "sha256 mismatch", status=400)
    partition = account_partition(
        module.config.public_origin,
        session["instance_id"],
        session["tenant_id"],
        session["subject"],
    )
    request_hash = sha256_jcs({"filename": file_part["filename"], "media_type": media, "sha256": sha})
    resource_identity = f"{params['key']}:{params['id']}"
    existing = module.store.get_receipt(
        partition, session["instance_id"], session["client_id"], "attachments.upload", resource_identity, request_id
    )
    if existing:
        if existing["request_hash"] != request_hash:
            raise ApiError("IDEMPOTENCY_CONFLICT", "idempotency key reused with different content", status=409)
        if parse_rfc3339(existing["expires_at"]) < utcnow():
            raise ApiError("IDEMPOTENCY_EXPIRED", "idempotency key expired", status=409)
        return 200, json.loads(existing["response_json"]), None
    if module.store.injections.get("fail_before_first_write") and module.store.write_count == 0:
        module.store.mark_observed("fail_before_first_write")
        raise RuntimeError("injected failure before first write")
    rec = module.host.store_upload(
        session["subject"],
        params["key"],
        params["id"],
        file_part["filename"],
        media,
        file_part["data"],
        sha,
    )
    if module.store.injections.get("fail_after_file_publish"):
        module.store.mark_observed("fail_after_file_publish")
        if hasattr(module.host, "forget_upload"):
            module.host.forget_upload(rec["upload_id"], keep_blob=True)
        raise RuntimeError("injected failure after file publish")
    public = {k: rec[k] for k in ("upload_id", "thread_id", "expertKey", "filename", "media_type", "bytes", "sha256", "expires_at", "state")}
    with module.store.txn():
        module.store.insert_upload(
            {
                "upload_id": rec["upload_id"],
                "owner_subject": session["subject"],
                "thread_id": params["id"],
                "expert_key": params["key"],
                "filename": rec["filename"],
                "media_type": rec["media_type"],
                "bytes": rec["bytes"],
                "sha256": rec["sha256"],
                "storage_path": rec.get("storage_path") or "",
                "state": rec["state"],
                "created_at": rfc3339(),
                "expires_at": rec["expires_at"],
            }
        )
        module.store.save_receipt(
            {
                "receipt_id": str(uuid4()),
                "account_partition": partition,
                "source_instance_id": session["instance_id"],
                "client_id": session["client_id"],
                "operation": "attachments.upload",
                "resource_identity": resource_identity,
                "request_id": request_id,
                "request_hash": request_hash,
                "status_code": 201,
                "response_json": json.dumps(public, ensure_ascii=False),
                "created_at": rfc3339(),
                "expires_at": later(RECEIPT_TTL_SECONDS),
            }
        )
    return 201, public, None


def ws_tickets(module: Any, params: dict[str, str], query: dict[str, str], headers: dict[str, str], body: bytes, scope: dict[str, Any]) -> tuple[int, Any, None]:
    session = _require_session(module, headers)
    data = _json(body)
    if set(data) != {"expertKey"}:
        raise ApiError("CONFIG_INVALID", "expertKey required", status=400)
    _require_expert(module, session, data["expertKey"], "chat")
    origin = _origin(headers, scope)
    client = module.config.client_by_id(session["client_id"])
    if client and origin and origin != client.extension_origin:
        raise ApiError("FORBIDDEN", "origin mismatch", status=403)
    ticket = new_token(prefix="wst1_", nbytes=32)
    now = rfc3339()
    expires = later(WS_TICKET_TTL_SECONDS)
    module.store.insert_ticket(
        {
            "ticket_hash": hash_secret(ticket),
            "sid": session["sid"],
            "client_id": session["client_id"],
            "expert_key": data["expertKey"],
            "instance_id": session["instance_id"],
            "origin": origin or (client.extension_origin if client else ""),
            "created_at": now,
            "expires_at": expires,
        }
    )
    ws_url = f"{module.ws_origin()}{API_PREFIX}/experts/{data['expertKey']}/chat/ws?ticket={ticket}"
    return 201, {"ticket": ticket, "expires_at": expires, "ws_url": ws_url}, None


def approvals(module: Any, params: dict[str, str], query: dict[str, str], headers: dict[str, str], body: bytes, scope: dict[str, Any]) -> tuple[int, Any, None]:
    session = _require_session(module, headers)
    expert = _require_expert(module, session, params["key"], "approve")
    if not expert["capabilities"]["approval_in_client"]:
        raise ApiError("CAPABILITY_UNAVAILABLE", "remote approval is not in-client", status=409)
    data = _json(body)
    required = {"pending_id", "decision_id", "decisions"}
    if set(data) != required:
        raise ApiError("CONFIG_INVALID", "invalid approval body", status=400)
    result = module.host.submit_approval(
        session["subject"],
        params["key"],
        params["id"],
        data["pending_id"],
        data["decision_id"],
        data["decisions"],
    )
    return 202, result, None


def approval_instructions(module: Any, params: dict[str, str], query: dict[str, str], headers: dict[str, str], body: bytes, scope: dict[str, Any]) -> tuple[int, Any, None]:
    session = _require_session(module, headers)
    _require_expert(module, session, params["key"], "read")
    pending_id = query.get("pending_id")
    if not pending_id:
        raise ApiError("CONFIG_INVALID", "pending_id required", status=400)
    return 200, module.host.get_approval_instructions(params["id"], pending_id), None
