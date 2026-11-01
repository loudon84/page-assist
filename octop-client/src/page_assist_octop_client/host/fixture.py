from __future__ import annotations

import hashlib
import threading
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from page_assist_octop_client.constants import (
    CONTEXT_UTF8_MAX,
    FILE_BYTES_MAX,
    FILES_PER_TURN_MAX,
    HISTORY_PAGE_SIZE,
    QUESTION_UTF8_MAX,
)
from page_assist_octop_client.errors import ApiError
from page_assist_octop_client.host.port import HostPort, HostUser, RuntimeState, TurnHandle
from page_assist_octop_client.jcs import canonical_json, sha256_hex
from page_assist_octop_client.timeutil import later, rfc3339


def _b64url(data: bytes) -> str:
    import base64

    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def expert_key(kind: str, **fields: str) -> str:
    payload = {"v": 1, "kind": kind, **fields}
    return "ex1_" + _b64url(canonical_json(payload).encode("utf-8"))


class FixtureHostPort:
    """In-process HostPort used by fixture acceptance. Not a product Octop host."""

    def __init__(self, root: Path, instance_id: str = "00000000-0000-4000-8000-000000000001") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.instance_id = instance_id
        self.host_build_id = "fixture-host-1"
        self._ready = True
        self._setup_complete = True
        self._worker_count = 1
        self._lock = threading.RLock()
        self.mounted: list[tuple[str, Callable]] = []
        self.auth_bypasses: list[str] = []
        self.start_hooks: list[Callable[[], None]] = []
        self.stop_hooks: list[Callable[[], None]] = []
        self.register_count = 0
        self.users = {
            "host_user": HostUser("host_user", "Host User"),
            "user_a": HostUser("user_a", "User A"),
            "user_b": HostUser("user_b", "User B"),
        }
        self.local_agent_id = "agent-local-alpha"
        self.hitl_agent_id = "agent-local-hitl"
        self.peer_instance_id = "00000000-0000-4000-8000-0000000000aa"
        self.personal_connection_id = "conn-personal-1"
        self.shared_connection_id = "conn-shared-1"
        self.experts: dict[str, dict[str, Any]] = {}
        self._seed_experts()
        self.threads: dict[str, dict[str, Any]] = {}
        self.messages: dict[str, list[dict[str, Any]]] = {}
        self.runtimes: dict[str, RuntimeState] = {}
        self.uploads: dict[str, dict[str, Any]] = {}
        self.pendings: dict[str, dict[str, Any]] = {}
        self.decisions: dict[str, dict[str, Any]] = {}
        self.bindings: dict[tuple[str, str], dict[str, Any]] = {}
        self.peer_online = True
        self.shared_users = ["group-shared"]
        self.dashboard_bindings: dict[str, str] = {
            key: sha256_hex(f"dashboard:{key}".encode()) for key in self.experts
        }
        self.cancelled: list[str] = []
        self._busy: set[str] = set()
        self.acl_revoked: set[tuple[str, str]] = set()
        self.fail_next_turn_ack = False
        self.hold_turn_until_history = False
        self.held_turns: set[str] = set()
        self.injection_observed: dict[str, bool] = {}

    def _seed_experts(self) -> None:
        local_key = expert_key("local", instance_id=self.instance_id, agent_id=self.local_agent_id)
        hitl_key = expert_key("local", instance_id=self.instance_id, agent_id=self.hitl_agent_id)
        personal_key = expert_key(
            "bridge",
            hub_instance_id=self.instance_id,
            connection_id=self.personal_connection_id,
            peer_instance_id=self.peer_instance_id,
            remote_agent_id="peer-agent-1",
        )
        shared_key = expert_key(
            "bridge",
            hub_instance_id=self.instance_id,
            connection_id=self.shared_connection_id,
            peer_instance_id="00000000-0000-4000-8000-0000000000bb",
            remote_agent_id="peer-shared-1",
        )
        self.experts[local_key] = self._expert(
            local_key, "Alpha Expert", "local", "本实例", True, "in_client"
        )
        self.experts[hitl_key] = self._expert(
            hitl_key, "HITL Expert", "local", "本实例", True, "in_client", hitl=True
        )
        self.experts[personal_key] = self._expert(
            personal_key, "Personal Peer Expert", "bridge_personal", "个人远端", False, "external_instructions"
        )
        self.experts[shared_key] = self._expert(
            shared_key, "Shared Bridge Expert", "bridge_shared", "共享连接", False, "none", available=False
        )
        self.local_key = local_key
        self.hitl_key = hitl_key
        self.personal_key = personal_key
        self.shared_key = shared_key

    def _expert(
        self,
        key: str,
        name: str,
        source_kind: str,
        label: str,
        approval_in_client: bool,
        approval_mode: str,
        hitl: bool = False,
        available: bool = True,
    ) -> dict[str, Any]:
        return {
            "expertKey": key,
            "name": name,
            "description": f"{name} fixture",
            "avatar": {"kind": "emoji", "value": "🤖"},
            "kind": "expert",
            "source": {"kind": source_kind, "label": label},
            "availability": "available" if available else "unsupported",
            "unavailable_reason": None if available else "SHARED_BRIDGE_UNSUPPORTED",
            "capabilities": {
                "create_thread": available,
                "chat": available,
                "attachments": available,
                "approval_in_client": approval_in_client,
                "approval_mode": approval_mode,
            },
            "_hitl": hitl,
        }

    def get_state_root(self) -> Path:
        return self.root

    def get_instance_id(self) -> str:
        return self.instance_id

    def get_host_build_id(self) -> str:
        return self.host_build_id

    def get_host_api_version(self) -> int:
        return 1

    def is_ready(self) -> bool:
        return self._ready

    def worker_count(self) -> int:
        return self._worker_count

    def is_setup_complete(self) -> bool:
        return self._setup_complete

    def get_db_path(self) -> Path:
        return self.root / "octop-business.sqlite"

    def lookup_user(self, subject: str) -> HostUser | None:
        return self.users.get(subject)

    def authenticate_login(self, subject: str) -> HostUser:
        user = self.users.get(subject)
        if not user or not user.enabled:
            raise ApiError("AUTH_CODE_INVALID", "user not enabled", status=400)
        return user

    def check_acl(self, subject: str, expert_key_value: str, action: str) -> bool:
        if (subject, expert_key_value) in self.acl_revoked:
            return False
        if expert_key_value not in self.experts:
            return False
        return True

    def list_experts(self, subject: str, source: str, q: str | None) -> list[dict[str, Any]]:
        items = []
        for expert in self.experts.values():
            kind = expert["source"]["kind"]
            if source == "local" and kind != "local":
                continue
            if source == "remote" and kind == "local":
                continue
            if q and q.lower() not in expert["name"].lower():
                continue
            if not self.check_acl(subject, expert["expertKey"], "read"):
                continue
            public = {k: v for k, v in expert.items() if not k.startswith("_")}
            items.append(public)
        items.sort(key=lambda e: (e["name"], e["expertKey"]))
        return items

    def get_expert_raw(self, expert_key_value: str) -> dict[str, Any] | None:
        return self.experts.get(expert_key_value)

    def get_expert(self, expert_key_value: str) -> dict[str, Any] | None:
        expert = self.experts.get(expert_key_value)
        if not expert:
            return None
        return {k: v for k, v in expert.items() if not k.startswith("_")}

    def create_thread(self, subject: str, expert_key_value: str, request_id: str) -> dict[str, Any]:
        now = rfc3339()
        thread_id = str(uuid4())
        thread = {
            "thread_id": thread_id,
            "expertKey": expert_key_value,
            "channel_type": "page_assist",
            "title": "",
            "created_at": now,
            "updated_at": now,
            "owner": subject,
            "source_kind": self.experts[expert_key_value]["source"]["kind"],
        }
        self.threads[thread_id] = thread
        self.messages[thread_id] = []
        self.runtimes[thread_id] = RuntimeState()
        return {**thread, "runtime": self.runtimes[thread_id].to_dict()}

    def forget_thread(self, thread_id: str) -> None:
        self.threads.pop(thread_id, None)
        self.messages.pop(thread_id, None)
        self.runtimes.pop(thread_id, None)
        self._busy.discard(thread_id)
        self.held_turns.discard(thread_id)

    def forget_upload(self, upload_id: str, *, keep_blob: bool = True) -> None:
        rec = self.uploads.pop(upload_id, None)
        if rec and not keep_blob:
            blob = self.root / rec["storage_path"] / "blob"
            try:
                blob.unlink()
            except OSError:
                pass

    def get_thread(self, thread_id: str) -> dict[str, Any] | None:
        thread = self.threads.get(thread_id)
        if not thread:
            return None
        return {**thread, "runtime": self.runtimes[thread_id].to_dict()}

    def list_threads(self, subject: str, expert_key_value: str) -> list[dict[str, Any]]:
        items = []
        for thread in self.threads.values():
            if thread["owner"] == subject and thread["expertKey"] == expert_key_value:
                items.append({**thread, "runtime": self.runtimes[thread["thread_id"]].to_dict()})
        items.sort(key=lambda t: (-_ts(t["updated_at"]), t["thread_id"]))
        return items

    def _finish_held_turn(self, thread_id: str) -> None:
        if thread_id not in self.held_turns:
            return
        runtime = self.runtimes[thread_id]
        text = "held-turn-completed"
        self.messages[thread_id].append(
            {
                "message_id": str(uuid4()),
                "order": len(self.messages[thread_id]),
                "role": "assistant",
                "parts": [{"kind": "text", "data": {"text": text}}],
                "created_at": rfc3339(),
                "client_request_id": None,
            }
        )
        runtime.state = "idle"
        runtime.last_outcome = "completed"
        self._busy.discard(thread_id)
        self.held_turns.discard(thread_id)
        self.injection_observed["complete_turn_during_history"] = True

    def get_history(self, thread_id: str, cursor: str | None) -> dict[str, Any]:
        self._finish_held_turn(thread_id)
        msgs = list(self.messages.get(thread_id, []))
        start = 0
        if cursor:
            try:
                start = int(cursor)
            except ValueError as exc:
                raise ApiError("CURSOR_STALE", "cursor expired", status=409) from exc
            if start < 0 or start > len(msgs):
                raise ApiError("CURSOR_STALE", "cursor expired", status=409)
        window = msgs[max(0, len(msgs) - HISTORY_PAGE_SIZE - start) : len(msgs) - start if start else None]
        if start:
            window = msgs[max(0, len(msgs) - start - HISTORY_PAGE_SIZE) : len(msgs) - start]
        else:
            window = msgs[-HISTORY_PAGE_SIZE:]
        next_cursor = None
        remaining = (len(msgs) - start) - len(window)
        if remaining > 0:
            next_cursor = str(start + len(window))
        revision = sha256_hex(f"{thread_id}:{len(msgs)}".encode())
        return {
            "thread_id": thread_id,
            "items": window,
            "next_cursor": next_cursor,
            "history_revision": revision,
            "runtime": self.runtimes[thread_id].to_dict(),
        }

    def accept_turn(
        self,
        subject: str,
        expert_key_value: str,
        thread_id: str,
        client_request_id: str,
        question: str,
        context: dict[str, Any] | None,
        upload_ids: list[str],
    ) -> TurnHandle:
        with self._lock:
            if thread_id in self._busy or self.runtimes[thread_id].state in (
                "running",
                "awaiting_approval",
            ):
                raise ApiError("TURN_BUSY", "该会话已有任务运行", status=409, details={"thread_id": thread_id})
            if len(question.encode("utf-8")) > QUESTION_UTF8_MAX:
                raise ApiError("INPUT_TOO_LARGE", "question too large", status=413)
            if context and len((context.get("text") or "").encode("utf-8")) > CONTEXT_UTF8_MAX:
                raise ApiError("INPUT_TOO_LARGE", "context too large", status=413)
            if len(upload_ids) > FILES_PER_TURN_MAX:
                raise ApiError("UPLOAD_TOO_LARGE", "too many files", status=413)
            turn_id = str(uuid4())
            self._busy.add(thread_id)
            runtime = self.runtimes[thread_id]
            runtime.state = "running"
            runtime.turn_id = turn_id
            now = rfc3339()
            order = len(self.messages[thread_id])
            user_parts: list[dict[str, Any]] = [{"kind": "text", "data": {"text": question}}]
            if context:
                user_parts.append({"kind": "text", "data": {"text": context.get("text", ""), "context": context}})
            for upload_id in upload_ids:
                user_parts.append({"kind": "attachment", "data": {"upload_id": upload_id}})
            self.messages[thread_id].append(
                {
                    "message_id": str(uuid4()),
                    "order": order,
                    "role": "user",
                    "parts": user_parts,
                    "created_at": now,
                    "client_request_id": client_request_id,
                }
            )
            expert = self.experts[expert_key_value]
            events: list[dict[str, Any]] = [
                {"type": "submission.accepted", "payload": {"status": "accepted"}},
                {"type": "turn.started", "payload": {"state": "running"}},
            ]
            if self.hold_turn_until_history:
                self.held_turns.add(thread_id)
                self.injection_observed["hold_turn_until_history"] = True
                if self.fail_next_turn_ack:
                    self.fail_next_turn_ack = False
                    handle = TurnHandle(turn_id=turn_id, thread_id=thread_id, status="accepted", events=events)
                    handle.status = "unknown"
                    return handle
                return TurnHandle(turn_id=turn_id, thread_id=thread_id, status="accepted", events=events)
            if expert.get("_hitl"):
                pending_id = str(uuid4())
                pending = {
                    "pending_id": pending_id,
                    "mode": "in_client",
                    "items": [
                        {
                            "item_id": "tool-1",
                            "kind": "tool",
                            "title": "Run search",
                            "detail": "Allow search tool?",
                            "allowed_decisions": ["approve", "reject"],
                            "fields": [],
                        }
                    ],
                }
                self.pendings[pending_id] = {
                    **pending,
                    "thread_id": thread_id,
                    "owner": subject,
                    "consumed": False,
                }
                runtime.state = "awaiting_approval"
                runtime.pending_id = pending_id
                events.append({"type": "approval.required", "payload": pending})
            elif expert["source"]["kind"] == "bridge_personal" and not self.peer_online:
                raise ApiError("PEER_UNAVAILABLE", "peer offline", status=503, retryable=True)
            else:
                text = f"echo:{question}"
                events.append({"type": "message.delta", "payload": {"stream_id": "s1", "text": text}})
                events.append(
                    {
                        "type": "tool.call",
                        "payload": {
                            "tool_call_id": "t1",
                            "name": "lookup",
                            "status": "running",
                            "arguments_summary": "q",
                        },
                    }
                )
                events.append(
                    {
                        "type": "tool.result",
                        "payload": {
                            "tool_call_id": "t1",
                            "name": "lookup",
                            "status": "succeeded",
                            "summary": "ok",
                            "upload_ids": [],
                        },
                    }
                )
                events.append(
                    {
                        "type": "usage",
                        "payload": {"input_tokens": 8, "output_tokens": 4, "total_tokens": 12},
                    }
                )
                self.messages[thread_id].append(
                    {
                        "message_id": str(uuid4()),
                        "order": order + 1,
                        "role": "assistant",
                        "parts": [{"kind": "text", "data": {"text": text}}],
                        "created_at": rfc3339(),
                        "client_request_id": client_request_id,
                    }
                )
                runtime.state = "idle"
                runtime.last_outcome = "completed"
                events.append({"type": "turn.ended", "payload": {"outcome": "completed", "runtime": runtime.to_dict()}})
                self._busy.discard(thread_id)
            self.threads[thread_id]["updated_at"] = rfc3339()
            if self.fail_next_turn_ack:
                self.fail_next_turn_ack = False
                handle = TurnHandle(turn_id=turn_id, thread_id=thread_id, status="accepted", events=events)
                handle.status = "unknown"
                return handle
            return TurnHandle(turn_id=turn_id, thread_id=thread_id, status="accepted", events=events)

    def cancel_turn(self, thread_id: str, expected_turn_id: str) -> dict[str, Any]:
        runtime = self.runtimes[thread_id]
        if runtime.turn_id != expected_turn_id:
            raise ApiError("TURN_CHANGED", "turn already changed", status=409)
        if runtime.state in ("idle", "interrupted") and runtime.last_outcome in (
            "completed",
            "cancelled",
            "failed",
        ):
            return {"status": "already_terminal", "turn_id": expected_turn_id}
        runtime.state = "idle"
        runtime.last_outcome = "cancelled"
        self._busy.discard(thread_id)
        self.cancelled.append(expected_turn_id)
        return {"status": "requested", "turn_id": expected_turn_id}

    def get_runtime(self, thread_id: str) -> RuntimeState:
        return self.runtimes[thread_id]

    def store_upload(
        self,
        subject: str,
        expert_key_value: str,
        thread_id: str,
        filename: str,
        media_type: str,
        data: bytes,
        sha256: str,
    ) -> dict[str, Any]:
        if ".." in filename or filename.startswith("/") or "\\" in filename:
            raise ApiError("UPLOAD_REF_FORBIDDEN", "illegal filename", status=403)
        if len(data) > FILE_BYTES_MAX:
            raise ApiError("UPLOAD_TOO_LARGE", "file too large", status=413)
        digest = hashlib.sha256(data).hexdigest()
        if digest != sha256:
            raise ApiError("UPLOAD_INCOMPLETE", "sha256 mismatch", status=400)
        upload_id = str(uuid4())
        rel = Path("inbound") / "page-assist" / subject[:16] / thread_id[:16] / upload_id
        dest = self.root / rel
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "blob").write_bytes(data)
        rec = {
            "upload_id": upload_id,
            "thread_id": thread_id,
            "expertKey": expert_key_value,
            "filename": Path(filename).name,
            "media_type": media_type,
            "bytes": len(data),
            "sha256": sha256,
            "expires_at": later(86400),
            "state": "ready",
            "owner": subject,
            "storage_path": str(rel),
        }
        self.uploads[upload_id] = rec
        return rec

    def attach_uploads(self, thread_id: str, upload_ids: list[str]) -> None:
        for upload_id in upload_ids:
            rec = self.uploads.get(upload_id)
            if rec and rec["thread_id"] == thread_id:
                rec["state"] = "attached"

    def submit_approval(
        self,
        subject: str,
        expert_key_value: str,
        thread_id: str,
        pending_id: str,
        decision_id: str,
        decisions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        pending = self.pendings.get(pending_id)
        if not pending or pending["thread_id"] != thread_id:
            raise ApiError("APPROVAL_STALE", "pending not found", status=409)
        if pending["owner"] != subject:
            raise ApiError("FORBIDDEN", "not owner", status=403)
        expert = self.experts[expert_key_value]
        if not expert["capabilities"]["approval_in_client"]:
            raise ApiError("CAPABILITY_UNAVAILABLE", "approval not in client", status=409)
        existing = self.decisions.get(decision_id)
        payload_hash = sha256_hex(canonical_json(decisions).encode())
        if existing:
            if existing["hash"] != payload_hash:
                raise ApiError("IDEMPOTENCY_CONFLICT", "decision mismatch", status=409)
            return {"decision_id": decision_id, "status": "accepted"}
        if pending["consumed"]:
            raise ApiError("APPROVAL_STALE", "pending consumed", status=409)
        pending["consumed"] = True
        self.decisions[decision_id] = {"hash": payload_hash, "count": 1}
        runtime = self.runtimes[thread_id]
        runtime.state = "idle"
        runtime.pending_id = None
        runtime.last_outcome = "completed"
        self._busy.discard(thread_id)
        self.messages[thread_id].append(
            {
                "message_id": str(uuid4()),
                "order": len(self.messages[thread_id]),
                "role": "assistant",
                "parts": [{"kind": "text", "data": {"text": "approved"}}],
                "created_at": rfc3339(),
                "client_request_id": None,
            }
        )
        return {"decision_id": decision_id, "status": "accepted"}

    def get_pending_approval(self, thread_id: str, pending_id: str) -> dict[str, Any] | None:
        pending = self.pendings.get(pending_id)
        if not pending or pending["thread_id"] != thread_id:
            return None
        return pending

    def get_approval_instructions(self, thread_id: str, pending_id: str) -> dict[str, Any]:
        return {
            "pending_id": pending_id,
            "source_label": "Octop Dashboard",
            "entry_url": "https://octop.example.internal/approvals",
            "instructions": "Complete this approval in Octop.",
        }

    def bridge_kind(self, expert_key_value: str) -> str:
        expert = self.experts.get(expert_key_value)
        if not expert:
            return "unknown"
        return expert["source"]["kind"]

    def bridge_call(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        allowed = {
            "identity",
            "capabilities",
            "catalog",
            "threads.list",
            "threads.create",
            "history",
            "upload",
            "chat.subscribe",
            "chat.send",
            "chat.cancel",
        }
        if operation not in allowed:
            raise ApiError("FORBIDDEN", "peer operation not allowed", status=403)
        if not self.peer_online:
            raise ApiError("PEER_UNAVAILABLE", "peer offline", status=503, retryable=True)
        return {"ok": True, "operation": operation}

    def mount_client_api(self, path: str, asgi_app: Callable) -> None:
        self.mounted.append((path, asgi_app))

    def register_auth_bypass(self, path_prefix: str) -> None:
        if path_prefix not in self.auth_bypasses:
            self.auth_bypasses.append(path_prefix)

    def on_start(self, callback: Callable[[], None]) -> None:
        self.start_hooks.append(callback)

    def on_stop(self, callback: Callable[[], None]) -> None:
        self.stop_hooks.append(callback)

    def dashboard_binding_digest(self, expert_key_value: str) -> str:
        return self.dashboard_bindings[expert_key_value]


def _ts(value: str) -> float:
    from page_assist_octop_client.timeutil import parse_rfc3339

    return parse_rfc3339(value).timestamp()
