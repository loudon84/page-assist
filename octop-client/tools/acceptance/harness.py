from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4

from page_assist_octop_client.auth.tokens import pkce_challenge
from page_assist_octop_client.host.fixture import FixtureHostPort
from page_assist_octop_client.integration.register import register, reset_registry
from page_assist_octop_client.testing import AsgiClient, WsSession

ORIGIN = "chrome-extension://abcdefghijklmnopqrstuvwxyz123456"
REDIRECT = "https://abcdefghijklmnopqrstuvwxyz123456.chromiumapp.org/"
CLIENT_ID = "page-assist-chrome"


def assert_eq(name: str, actual: Any, expected: Any) -> dict[str, Any]:
    return {"name": name, "passed": actual == expected, "expected": expected, "actual": actual}


def assert_true(name: str, actual: Any) -> dict[str, Any]:
    return {"name": name, "passed": bool(actual), "expected": True, "actual": bool(actual)}


def assert_in(name: str, actual: Any, expected_set: list[Any] | set[Any]) -> dict[str, Any]:
    return {"name": name, "passed": actual in expected_set, "expected": list(expected_set), "actual": actual}


class Harness:
    def __init__(self, tmp: Path) -> None:
        reset_registry()
        self.tmp = Path(tmp)
        self.host = FixtureHostPort(self.tmp)
        self.cfg = {
            "schema_version": 1,
            "enabled": True,
            "public_origin": "https://octop.example.internal",
            "allowed_clients": [
                {
                    "client_id": CLIENT_ID,
                    "extension_origin": ORIGIN,
                    "redirect_uri": REDIRECT,
                }
            ],
            "state_root": str(self.tmp),
            "host_api_version": 1,
            "worker_count": 1,
            "session_ttl_seconds": 28800,
            "log_level": "INFO",
            "fixture_mode": True,
        }
        self.module = register(None, self.host, self.cfg)
        self.client = AsgiClient(self.module.asgi)

    def close(self) -> None:
        self.module.stop()

    def inject(self, **flags: Any) -> None:
        self.module.store.injections.update(flags)
        self.module.store.write_count = 0
        self.module.store.injection_observed.clear()

    def observed(self, key: str) -> bool:
        return bool(self.module.store.injection_observed.get(key) or self.host.injection_observed.get(key))

    def auth(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}", "Origin": ORIGIN}

    async def login(self, subject: str = "host_user") -> tuple[str, dict[str, Any]]:
        import base64
        import secrets
        from urllib.parse import parse_qs, urlparse

        verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
        state = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
        status, body = await self.client.json(
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
        if status != 201:
            raise RuntimeError(f"transaction failed: {status} {body}")
        url = body["authorization_url"] + f"&subject={subject}"
        _st, _resp, headers = await self.client.request("GET", url.replace("https://octop.example.internal", ""))
        loc = headers.get("location", "")
        code = parse_qs(urlparse(loc).query).get("code", [None])[0]
        status, exch = await self.client.json(
            "POST",
            "/api/client/v1/auth/exchange",
            json_body={
                "client_id": CLIENT_ID,
                "redirect_uri": REDIRECT,
                "code": code,
                "code_verifier": verifier,
            },
        )
        if status != 200:
            raise RuntimeError(f"exchange failed: {status} {exch}")
        return exch["access_token"], exch["session"]

    async def experts(self, token: str) -> list[dict[str, Any]]:
        status, body = await self.client.json("GET", "/api/client/v1/experts", headers=self.auth(token))
        if status != 200:
            raise RuntimeError(f"experts failed: {status} {body}")
        return body["items"]

    def local(self, items: list[dict[str, Any]], name: str | None = None) -> dict[str, Any]:
        if name:
            return next(e for e in items if e["name"] == name)
        return next(e for e in items if e["source"]["kind"] == "local" and e["name"] == "Alpha Expert")

    async def create_thread(self, token: str, expert_key: str, request_id: str | None = None) -> tuple[int, Any]:
        return await self.client.json(
            "POST",
            f"/api/client/v1/experts/{expert_key}/threads",
            json_body={},
            headers={**self.auth(token), "Idempotency-Key": request_id or str(uuid4())},
        )

    def multipart(self, blob: bytes, filename: str = "a.txt", media: str = "text/plain") -> tuple[bytes, str, str]:
        digest = hashlib.sha256(blob).hexdigest()
        boundary = "----paocboundary"
        body = (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: {media}\r\n\r\n".encode()
            + blob
            + f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"sha256\"\r\n\r\n{digest}\r\n--{boundary}--\r\n".encode()
        )
        return body, boundary, digest

    async def upload(self, token: str, expert_key: str, thread_id: str, blob: bytes, key: str | None = None) -> tuple[int, Any]:
        body, boundary, _digest = self.multipart(blob)
        status, raw, _ = await self.client.request(
            "POST",
            f"/api/client/v1/experts/{expert_key}/threads/{thread_id}/uploads",
            body=body,
            content_type=f"multipart/form-data; boundary={boundary}",
            headers={**self.auth(token), "Idempotency-Key": key or str(uuid4())},
        )
        parsed = json.loads(raw) if raw else None
        return status, parsed

    async def ticket(self, token: str, expert_key: str) -> dict[str, Any]:
        status, body = await self.client.json(
            "POST",
            "/api/client/v1/ws-tickets",
            json_body={"expertKey": expert_key},
            headers=self.auth(token),
        )
        if status != 201:
            raise RuntimeError(f"ticket failed: {status} {body}")
        return body

    async def connect_ws(self, token: str, expert_key: str) -> tuple[WsSession, dict[str, Any]]:
        body = await self.ticket(token, expert_key)
        path = f"/api/client/v1/experts/{expert_key}/chat/ws?ticket={body['ticket']}"
        ws = await self.client.websocket(path, headers={"Origin": ORIGIN})
        return ws, body

    def counts(self) -> dict[str, int]:
        store = self.module.store
        return {
            "sessions": store.count("paoc_sessions"),
            "threads": store.count("paoc_thread_metadata"),
            "receipts": store.count("paoc_operation_receipts"),
            "uploads": store.count("paoc_uploads"),
            "host_threads": len(self.host.threads),
            "host_uploads": len(self.host.uploads),
        }


async def with_harness(fn: Any) -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        h = Harness(Path(tmp))
        try:
            return await fn(h)
        finally:
            h.close()
