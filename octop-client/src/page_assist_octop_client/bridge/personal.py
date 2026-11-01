from __future__ import annotations

from typing import Any
from uuid import uuid4

from page_assist_octop_client.errors import ApiError
from page_assist_octop_client.timeutil import rfc3339


class BridgeService:
    def __init__(self, module: Any) -> None:
        self.module = module

    def ensure_personal_binding(self, session: dict[str, Any], expert: dict[str, Any]) -> None:
        kind = expert["source"]["kind"]
        if kind == "bridge_shared":
            raise ApiError("SHARED_BRIDGE_UNSUPPORTED", "shared bridge private chat is not supported", status=403)
        if kind != "bridge_personal":
            return
        host = self.module.host
        connection_id = getattr(host, "personal_connection_id", "conn-personal-1")
        if getattr(host, "shared_users", None):
            shared = host.shared_users if connection_id == getattr(host, "shared_connection_id", "") else []
            if shared:
                raise ApiError("SHARED_BRIDGE_UNSUPPORTED", "connection has shared users", status=403)
        existing = self.module.store.get_binding(host.get_instance_id(), session["subject"], connection_id)
        peer_subject = "peer_user"
        peer_instance = getattr(host, "peer_instance_id", "peer")
        if existing and (
            existing["peer_subject"] != peer_subject or existing["peer_instance_id"] != peer_instance
        ):
            self.module.store.invalidate_binding(existing["binding_id"], rfc3339())
            raise ApiError("PERSONAL_BINDING_REQUIRED", "peer identity changed", status=403)
        other = self.module.store.conn.execute(
            """
            SELECT * FROM paoc_personal_bindings
            WHERE peer_instance_id=? AND peer_subject=? AND invalidated_at IS NULL
              AND NOT (hub_instance_id=? AND hub_subject=?)
            """,
            (peer_instance, peer_subject, host.get_instance_id(), session["subject"]),
        ).fetchone()
        if other:
            raise ApiError("PERSONAL_BINDING_REQUIRED", "peer already bound to another hub user", status=403)
        if existing is None:
            self.module.store.upsert_binding(
                {
                    "binding_id": str(uuid4()),
                    "hub_instance_id": host.get_instance_id(),
                    "hub_subject": session["subject"],
                    "connection_id": connection_id,
                    "peer_instance_id": peer_instance,
                    "peer_subject": peer_subject,
                    "binding_revision": 1,
                    "created_at": rfc3339(),
                }
            )
        host.bridge_call("identity", {"subject": session["subject"]})
