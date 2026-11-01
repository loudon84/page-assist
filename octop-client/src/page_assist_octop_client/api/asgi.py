from __future__ import annotations

import json
import re
from typing import Any, Callable
from urllib.parse import parse_qs
from uuid import uuid4

from page_assist_octop_client.constants import API_PREFIX
from page_assist_octop_client.errors import ApiError, http_status_for

Receive = Callable
Send = Callable


def json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


async def read_body(receive: Receive) -> bytes:
    chunks = bytearray()
    more = True
    while more:
        message = await receive()
        chunks.extend(message.get("body", b""))
        more = bool(message.get("more_body", False))
    return bytes(chunks)


async def send_http(send: Send, status: int, body: bytes, headers: list[tuple[bytes, bytes]] | None = None) -> None:
    hdrs = [
        (b"content-type", b"application/json; charset=utf-8"),
        (b"cache-control", b"no-store"),
    ]
    if headers:
        hdrs.extend(headers)
    await send({"type": "http.response.start", "status": status, "headers": hdrs})
    await send({"type": "http.response.body", "body": body})


async def send_error(send: Send, err: ApiError) -> None:
    await send_http(send, err.status or http_status_for(err.code), json_bytes(err.to_body()))


ROUTE_SPECS: list[tuple[str, str, str]] = [
    ("GET", r"^/capabilities$", "capabilities"),
    ("POST", r"^/auth/transactions$", "auth_transactions"),
    ("POST", r"^/auth/exchange$", "auth_exchange"),
    ("GET", r"^/session$", "get_session"),
    ("DELETE", r"^/session$", "delete_session"),
    ("GET", r"^/experts$", "list_experts"),
    ("GET", r"^/experts/(?P<key>[^/]+)/threads$", "list_threads"),
    ("POST", r"^/experts/(?P<key>[^/]+)/threads$", "create_thread"),
    ("GET", r"^/experts/(?P<key>[^/]+)/threads/(?P<id>[^/]+)/history$", "get_history"),
    ("POST", r"^/experts/(?P<key>[^/]+)/threads/(?P<id>[^/]+)/uploads$", "upload"),
    ("POST", r"^/ws-tickets$", "ws_tickets"),
    ("POST", r"^/experts/(?P<key>[^/]+)/threads/(?P<id>[^/]+)/approvals$", "approvals"),
    ("GET", r"^/experts/(?P<key>[^/]+)/threads/(?P<id>[^/]+)/approval-instructions$", "approval_instructions"),
]


class ClientApiASGI:
    def __init__(self, module: Any, inner: Callable | None = None) -> None:
        self.module = module
        self.inner = inner
        self.routes = [(method, re.compile(pattern), name) for method, pattern, name in ROUTE_SPECS]

    async def __call__(self, scope: dict[str, Any], receive: Receive, send: Send) -> None:
        path = scope.get("path", "")
        if scope["type"] == "websocket" and path.startswith(f"{API_PREFIX}/experts/") and path.endswith("/chat/ws"):
            from page_assist_octop_client.api.ws import handle_ws

            await handle_ws(self.module, scope, receive, send)
            return
        if scope["type"] == "http" and path.startswith(API_PREFIX):
            await self._handle_http(scope, receive, send)
            return
        if scope["type"] == "http" and path.startswith("/__fixture__/") and self.module.config.fixture_mode:
            from page_assist_octop_client.api.fixture_login import handle_fixture

            await handle_fixture(self.module, scope, receive, send)
            return
        if self.inner is not None:
            await self.inner(scope, receive, send)
            return
        if scope["type"] == "http":
            await send_http(send, 404, json_bytes({"error": {"code": "NOT_FOUND", "message": "not found", "retryable": False, "request_id": str(uuid4()), "details": {}}}))
            return

    async def _handle_http(self, scope: dict[str, Any], receive: Receive, send: Send) -> None:
        from page_assist_octop_client.api import handlers

        method = scope.get("method", "GET").upper()
        rel = scope.get("path", "")[len(API_PREFIX) :] or "/"
        query = {k: v[-1] for k, v in parse_qs(scope.get("query_string", b"").decode()).items()}
        headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
        match_name = None
        params: dict[str, str] = {}
        for route_method, pattern, name in self.routes:
            if route_method != method:
                continue
            matched = pattern.match(rel)
            if matched:
                match_name = name
                params = matched.groupdict()
                break
        body = await read_body(receive)
        try:
            if not self.module.enabled_ready and match_name not in (None,):
                if not self.module.config.enabled:
                    raise ApiError("CLIENT_MODULE_DISABLED", "module disabled", status=503)
                if not self.module.ready:
                    raise ApiError("CLIENT_MODULE_UNAVAILABLE", "module not ready", status=503)
            if match_name is None:
                raise ApiError("INVALID_ROUTE", "unknown client route", status=404)
            result = handlers.dispatch(self.module, match_name, method, params, query, headers, body, scope)
            status, payload, extra_headers = result
            raw = b"" if payload is None else json_bytes(payload)
            await send_http(send, status, raw, extra_headers)
        except ApiError as err:
            await send_error(send, err)
        except Exception:
            err = ApiError("STORAGE_UNAVAILABLE", "internal error", status=503, retryable=True)
            await send_error(send, err)
