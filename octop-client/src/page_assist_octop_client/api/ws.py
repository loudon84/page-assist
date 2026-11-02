from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs
from uuid import uuid4

from page_assist_octop_client.auth.tokens import hash_secret
from page_assist_octop_client.constants import API_PREFIX, TURN_JSON_MAX, WS_CLOSE_EXPIRED, WS_CLOSE_REVOKED
from page_assist_octop_client.errors import ApiError
from page_assist_octop_client.timeutil import parse_rfc3339, rfc3339, utcnow


async def handle_ws(module: Any, scope: dict[str, Any], receive: Any, send: Any) -> None:
    path = scope.get("path", "")
    query = {k: v[-1] for k, v in parse_qs(scope.get("query_string", b"").decode()).items()}
    headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
    origin = headers.get("origin", "")
    ticket = query.get("ticket", "")
    prefix = f"{API_PREFIX}/experts/"
    rest = path[len(prefix) :]
    expert_key = rest[: -len("/chat/ws")]
    try:
        session_row = _consume_ticket(module, ticket, expert_key, origin)
    except ApiError as err:
        await send({"type": "websocket.http.response.start", "status": 401, "headers": []})
        await send({"type": "websocket.http.response.body", "body": json.dumps(err.to_body()).encode()})
        return
    await send({"type": "websocket.accept"})
    connection_id = str(uuid4())
    seq = 0
    module.register_connection(session_row["sid"], connection_id, send)

    async def emit(
        event_type: str,
        payload: dict[str, Any],
        thread_id: str | None = None,
        turn_id: str | None = None,
        client_request_id: str | None = None,
    ) -> None:
        nonlocal seq
        seq += 1
        event = {
            "v": 1,
            "connection_id": connection_id,
            "seq": seq,
            "type": event_type,
            "thread_id": thread_id,
            "turn_id": turn_id,
            "client_request_id": client_request_id,
            "payload": payload,
        }
        await send({"type": "websocket.send", "text": json.dumps(event, ensure_ascii=False)})

    try:
        while True:
            message = await receive()
            mtype = message.get("type")
            if mtype == "websocket.disconnect":
                break
            if mtype != "websocket.receive":
                continue
            text = message.get("text")
            if text is None and message.get("bytes"):
                text = message["bytes"].decode("utf-8")
            if not text:
                continue
            try:
                cmd = json.loads(text)
            except json.JSONDecodeError:
                await emit("error", ApiError("CONFIG_INVALID", "invalid json").to_body()["error"])
                continue
            try:
                await _handle_command(module, session_row, expert_key, cmd, emit, send)
            except ApiError as err:
                await emit("error", err.to_body()["error"], cmd.get("thread_id"))
                if err.code == "TURN_BUSY":
                    continue
    finally:
        module.unregister_connection(connection_id)


def _consume_ticket(module: Any, ticket: str, expert_key: str, origin: str) -> dict[str, Any]:
    if not ticket:
        raise ApiError("AUTH_REQUIRED", "ticket required", status=401, ws_close=WS_CLOSE_EXPIRED)
    row = module.store.consume_ticket(hash_secret(ticket), rfc3339())
    if row is None:
        raise ApiError("AUTH_REQUIRED", "ticket invalid", status=401, ws_close=WS_CLOSE_EXPIRED)
    if row.get("_replay"):
        raise ApiError("AUTH_REQUIRED", "ticket already used", status=401, ws_close=WS_CLOSE_EXPIRED)
    if parse_rfc3339(row["expires_at"]) < utcnow():
        raise ApiError("SESSION_EXPIRED", "ticket expired", status=401, ws_close=WS_CLOSE_EXPIRED)
    if row["expert_key"] != expert_key:
        raise ApiError("FORBIDDEN", "ticket expert mismatch", status=403, ws_close=WS_CLOSE_REVOKED)
    session = module.store.get_session(row["sid"])
    if session is None or session["revoked_at"] is not None:
        raise ApiError("SESSION_REVOKED", "session revoked", status=401, ws_close=WS_CLOSE_REVOKED)
    if parse_rfc3339(session["expires_at"]) < utcnow():
        raise ApiError("SESSION_EXPIRED", "session expired", status=401, ws_close=WS_CLOSE_EXPIRED)
    client = module.config.client_by_id(session["client_id"])
    if origin and client and origin != client.extension_origin and origin != row["origin"]:
        raise ApiError("FORBIDDEN", "origin mismatch", status=403, ws_close=WS_CLOSE_REVOKED)
    if not module.host.check_acl(session["subject"], expert_key, "chat"):
        raise ApiError("FORBIDDEN", "acl revoked", status=403, ws_close=WS_CLOSE_REVOKED)
    session = dict(session)
    session["scopes"] = json.loads(session["scopes"]) if isinstance(session["scopes"], str) else session["scopes"]
    return session


async def _handle_command(module: Any, session: dict[str, Any], expert_key: str, cmd: dict[str, Any], emit: Any, send: Any) -> None:
    fresh = module.store.get_session(session["sid"])
    if fresh is None or fresh["revoked_at"] is not None or session["sid"] in module.revoked_sids:
        raise ApiError("SESSION_REVOKED", "session revoked", status=401, ws_close=WS_CLOSE_REVOKED)
    if not module.host.check_acl(session["subject"], expert_key, "chat"):
        raise ApiError("FORBIDDEN", "acl revoked", status=403, ws_close=WS_CLOSE_REVOKED)
    if cmd.get("v") != 1:
        raise ApiError("PROTOCOL_INCOMPATIBLE", "command v must be 1", status=426)
    ctype = cmd.get("type")
    request_id = cmd.get("request_id")
    thread_id = cmd.get("thread_id")
    payload = cmd.get("payload") or {}
    allowed = {"subscribe", "user_turn", "cancel", "ping"}
    if ctype not in allowed:
        raise ApiError("PROTOCOL_INCOMPATIBLE", "unknown command", status=426)
    if ctype == "ping":
        await emit("pong", {"nonce": str(payload.get("nonce", ""))[:64], "server_time": rfc3339()})
        return
    if not thread_id:
        raise ApiError("CONFIG_INVALID", "thread_id required", status=400)
    thread = module.host.get_thread(thread_id)
    if thread is None or thread["owner"] != session["subject"] or thread["expertKey"] != expert_key:
        raise ApiError("THREAD_NOT_FOUND", "thread not found", status=404)
    if ctype == "subscribe":
        runtime = module.host.get_runtime(thread_id).to_dict()
        ack = {"request_id": request_id, "thread_id": thread_id, "runtime": runtime}
        await send({"type": "websocket.send", "text": json.dumps({"v": 1, "type": "subscribe.ok", **ack})})
        await emit("thread.status", {"runtime": runtime, "history_revision": "0"}, thread_id)
        return
    if ctype == "cancel":
        expected = payload.get("expected_turn_id")
        result = module.host.cancel_turn(thread_id, expected)
        receipt = {
            "request_id": request_id,
            "thread_id": thread_id,
            "turn_id": result["turn_id"],
            "status": result["status"],
        }
        await send({"type": "websocket.send", "text": json.dumps(receipt)})
        return
    if ctype == "user_turn":
        extra = set(payload) - {"question", "context", "upload_ids"}
        if extra:
            raise ApiError("CONFIG_INVALID", "forbidden turn fields", status=400, details={"fields": sorted(extra)})
        question = payload.get("question") or ""
        context = payload.get("context")
        upload_ids = payload.get("upload_ids") or []
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        if len(raw) > TURN_JSON_MAX:
            raise ApiError("INPUT_TOO_LARGE", "turn json too large", status=413)
        if not question and not context and not upload_ids:
            raise ApiError("INPUT_EMPTY", "empty input", status=400)
        handle = module.host.accept_turn(
            session["subject"],
            expert_key,
            thread_id,
            request_id,
            question,
            context,
            upload_ids,
        )
        if upload_ids:
            module.host.attach_uploads(thread_id, upload_ids)
            for uid in upload_ids:
                module.store.mark_upload_attached(uid)
        if handle.status == "unknown":
            raise ApiError("RESULT_UNKNOWN", "turn accepted but ack lost", status=409, retryable=False)
        receipt = {
            "request_id": request_id,
            "thread_id": thread_id,
            "turn_id": handle.turn_id,
            "status": "accepted",
        }
        await send({"type": "websocket.send", "text": json.dumps(receipt)})
        for event in handle.events:
            await emit(
                event["type"],
                event["payload"],
                thread_id,
                handle.turn_id,
                request_id,
            )
        return
    raise ApiError("PROTOCOL_INCOMPATIBLE", "unhandled command", status=426)
