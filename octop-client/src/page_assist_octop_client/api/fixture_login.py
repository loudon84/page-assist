from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs, urlencode
from uuid import uuid4

from page_assist_octop_client.api.asgi import json_bytes, read_body, send_http
from page_assist_octop_client.auth.tokens import hash_secret, new_token
from page_assist_octop_client.constants import AUTH_CODE_TTL_SECONDS
from page_assist_octop_client.errors import ApiError
from page_assist_octop_client.timeutil import later, parse_rfc3339, rfc3339, utcnow


async def handle_fixture(module: Any, scope: dict[str, Any], receive: Any, send: Any) -> None:
    path = scope.get("path", "")
    query = {k: v[-1] for k, v in parse_qs(scope.get("query_string", b"").decode()).items()}
    await read_body(receive)
    if path != "/__fixture__/login":
        await send_http(send, 404, json_bytes({"error": "not found"}))
        return
    tx_id = query.get("transaction_id")
    subject = query.get("subject", "host_user")
    if not tx_id:
        await send_http(send, 400, json_bytes({"error": "missing transaction"}))
        return
    tx = module.store.get_transaction(tx_id)
    if tx is None or parse_rfc3339(tx["expires_at"]) < utcnow():
        await send_http(send, 400, json_bytes({"error": "transaction expired"}))
        return
    user = module.host.lookup_user(subject)
    if user is None:
        await send_http(send, 400, json_bytes({"error": "unknown user"}))
        return
    code = new_token(prefix="ac1_", nbytes=32)
    module.store.insert_code(
        {
            "code_hash": hash_secret(code),
            "transaction_id": tx_id,
            "client_id": tx["client_id"],
            "redirect_uri": tx["redirect_uri"],
            "subject": user.id,
            "display_name": user.display_name,
            "created_at": rfc3339(),
            "expires_at": later(AUTH_CODE_TTL_SECONDS),
        }
    )
    loc = tx["redirect_uri"]
    sep = "&" if "?" in loc else "?"
    loc = f"{loc}{sep}{urlencode({'code': code, 'state': tx['state']})}"
    await send_http(send, 302, b"", [(b"location", loc.encode())])
