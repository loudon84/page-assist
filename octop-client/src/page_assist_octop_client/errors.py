from __future__ import annotations

from typing import Any
from uuid import uuid4


class ApiError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        status: int = 400,
        retryable: bool = False,
        details: dict[str, Any] | None = None,
        request_id: str | None = None,
        ws_close: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.retryable = retryable
        self.details = details or {}
        self.request_id = request_id or str(uuid4())
        self.ws_close = ws_close

    def to_body(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "retryable": self.retryable,
                "request_id": self.request_id,
                "details": self.details,
            }
        }


def http_status_for(code: str, default: int = 400) -> int:
    mapping = {
        "CONFIG_INVALID": 400,
        "INSECURE_ENDPOINT": 400,
        "PROTOCOL_INCOMPATIBLE": 426,
        "CAPABILITY_UNAVAILABLE": 409,
        "AUTH_CANCELLED": 400,
        "AUTH_STATE_MISMATCH": 400,
        "AUTH_CODE_INVALID": 400,
        "AUTH_REQUIRED": 401,
        "SESSION_EXPIRED": 401,
        "SESSION_REVOKED": 401,
        "FORBIDDEN": 403,
        "EXPERT_NOT_FOUND": 404,
        "THREAD_NOT_FOUND": 404,
        "SHARED_BRIDGE_UNSUPPORTED": 403,
        "PERSONAL_BINDING_REQUIRED": 403,
        "INVALID_ROUTE": 400,
        "REQUEST_IN_FLIGHT": 409,
        "TURN_BUSY": 409,
        "RESULT_UNKNOWN": 409,
        "CURSOR_STALE": 409,
        "STALE_ACCOUNT_EPOCH": 409,
        "TURN_CHANGED": 409,
        "NETWORK_UNAVAILABLE": 503,
        "PEER_UNAVAILABLE": 503,
        "TIMEOUT": 504,
        "RATE_LIMITED": 429,
        "INPUT_EMPTY": 400,
        "INPUT_TOO_LARGE": 413,
        "CONTEXT_CAPTURE_DENIED": 400,
        "UNSUPPORTED_MEDIA": 415,
        "UPLOAD_TOO_LARGE": 413,
        "UPLOAD_INCOMPLETE": 400,
        "UPLOAD_REF_FORBIDDEN": 403,
        "IDEMPOTENCY_CONFLICT": 409,
        "IDEMPOTENCY_EXPIRED": 409,
        "APPROVAL_STALE": 409,
        "APPROVAL_RESULT_UNKNOWN": 409,
        "STORAGE_UNAVAILABLE": 503,
        "STORAGE_CLEANUP_REQUIRED": 503,
        "MIGRATION_BLOCKED": 409,
        "CLIENT_MODULE_DISABLED": 503,
        "CLIENT_MODULE_UNAVAILABLE": 503,
    }
    return mapping.get(code, default)
