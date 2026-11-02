from __future__ import annotations

PROTOCOL_MAJOR = 1
PROTOCOL_MINOR = 1
API_PREFIX = "/api/client/v1"
TOKEN_PREFIX = "octopc1_"
EXPERT_KEY_PREFIX = "ex1_"
SESSION_TTL_SECONDS = 28800
AUTH_TRANSACTION_TTL_SECONDS = 600
AUTH_CODE_TTL_SECONDS = 60
WS_TICKET_TTL_SECONDS = 30
RECEIPT_TTL_SECONDS = 86400
UPLOAD_TTL_SECONDS = 86400
CURSOR_TTL_SECONDS = 600
PAGE_SIZE = 50
HISTORY_PAGE_SIZE = 50
QUESTION_UTF8_MAX = 32768
CONTEXT_UTF8_MAX = 65536
TURN_JSON_MAX = 131072
FILE_BYTES_MAX = 10485760
FILES_PER_TURN_MAX = 5
FILES_TOTAL_MAX = 20971520
CONTEXT_CODEPOINTS_MAX = 20000
DEFAULT_QUESTION = "请分析这些材料。"
ALLOWED_SCOPES = (
    "experts:read",
    "threads:read",
    "threads:create",
    "chat:send",
    "chat:cancel",
    "uploads:write",
    "approvals:write",
)
CORE_FEATURES = (
    "catalog_v1",
    "independent_threads",
    "history_v1",
    "chat_ws_v1",
    "uploads_v1",
    "revocable_sessions",
    "runtime_revision_v1",
)
ALLOWED_MEDIA = {
    "image/png": "png",
    "image/jpeg": "jpeg",
    "image/webp": "webp",
    "application/pdf": "pdf",
    "text/plain": "txt",
    "text/markdown": "markdown",
    "text/csv": "csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}
WS_CLOSE_EXPIRED = 4401
WS_CLOSE_REVOKED = 4403
