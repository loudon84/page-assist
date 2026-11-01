from __future__ import annotations

import asyncio
import json
from typing import Any
from uuid import uuid4


class WsSession:
    def __init__(self, app: Any, path: str, query: str, headers: dict[str, str]) -> None:
        self.app = app
        self.path = path
        self.query = query
        self.headers = headers
        self.inbox: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self.outbox: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self.task: asyncio.Task[None] | None = None

    async def connect(self) -> "WsSession":
        hdrs = [(k.lower().encode(), v.encode()) for k, v in self.headers.items()]
        scope = {
            "type": "websocket",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "scheme": "wss",
            "path": self.path,
            "raw_path": self.path.encode(),
            "query_string": self.query.encode(),
            "headers": hdrs,
            "client": ("127.0.0.1", 1234),
            "server": ("octop.example.internal", 443),
            "subprotocols": [],
        }

        async def receive() -> dict[str, Any]:
            return await self.inbox.get()

        async def send(message: dict[str, Any]) -> None:
            await self.outbox.put(message)

        self.task = asyncio.create_task(self.app(scope, receive, send))
        first = await asyncio.wait_for(self.outbox.get(), 5)
        if first.get("type") != "websocket.accept":
            raise RuntimeError(f"websocket not accepted: {first}")
        return self

    async def send_json(self, payload: dict[str, Any]) -> None:
        await self.inbox.put({"type": "websocket.receive", "text": json.dumps(payload)})

    async def recv_json(self, timeout: float = 5) -> dict[str, Any]:
        message = await asyncio.wait_for(self.outbox.get(), timeout)
        text = message.get("text")
        if text:
            return json.loads(text)
        return message

    async def close(self) -> None:
        await self.inbox.put({"type": "websocket.disconnect", "code": 1000})
        if self.task is not None:
            await asyncio.wait_for(self.task, 5)


class AsgiClient:
    def __init__(self, app: Any) -> None:
        self.app = app

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
        content_type: str | None = None,
    ) -> tuple[int, bytes, dict[str, str]]:
        hdrs = [(b"content-type", (content_type or "application/json").encode())]
        for key, value in (headers or {}).items():
            hdrs.append((key.lower().encode(), value.encode()))
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")
        payload = body or b""
        sent: list[dict[str, Any]] = []

        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": payload, "more_body": False}

        async def send(message: dict[str, Any]) -> None:
            sent.append(message)

        query = b""
        if "?" in path:
            path, q = path.split("?", 1)
            query = q.encode()
        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method.upper(),
            "scheme": "https",
            "path": path,
            "raw_path": path.encode(),
            "query_string": query,
            "headers": hdrs,
            "client": ("127.0.0.1", 1234),
            "server": ("octop.example.internal", 443),
        }
        await self.app(scope, receive, send)
        status = 500
        resp_headers: dict[str, str] = {}
        resp_body = bytearray()
        for message in sent:
            if message["type"] == "http.response.start":
                status = int(message["status"])
                resp_headers = {k.decode(): v.decode() for k, v in message.get("headers", [])}
            elif message["type"] == "http.response.body":
                resp_body.extend(message.get("body", b""))
        return status, bytes(resp_body), resp_headers

    async def json(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, Any]:
        status, body, _ = await self.request(method, path, json_body=json_body, headers=headers)
        if not body:
            return status, None
        return status, json.loads(body.decode("utf-8"))

    async def websocket(self, path: str, headers: dict[str, str] | None = None) -> WsSession:
        query = ""
        if "?" in path:
            path, query = path.split("?", 1)
        session = WsSession(self.app, path, query, headers or {})
        return await session.connect()

    async def ping(self, ws: WsSession, nonce: str = "n1") -> dict[str, Any]:
        await ws.send_json(
            {
                "v": 1,
                "type": "ping",
                "request_id": str(uuid4()),
                "thread_id": None,
                "payload": {"nonce": nonce},
            }
        )
        return await ws.recv_json()
