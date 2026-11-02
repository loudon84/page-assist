from __future__ import annotations

SCHEMA_VERSION = 2
SCHEMA_CHECKSUM = "paoc-schema-v2"

MIGRATIONS: list[tuple[int, str]] = [
    (
        1,
        """
CREATE TABLE IF NOT EXISTS paoc_schema_version (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  version INTEGER NOT NULL,
  checksum TEXT NOT NULL,
  applied_at TEXT NOT NULL,
  reader_min INTEGER NOT NULL,
  writer_min INTEGER NOT NULL,
  application_count INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS paoc_sessions (
  sid TEXT PRIMARY KEY,
  token_sha256 TEXT NOT NULL UNIQUE,
  instance_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  subject TEXT NOT NULL,
  display_name TEXT NOT NULL,
  client_id TEXT NOT NULL,
  scopes TEXT NOT NULL,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  revoked_at TEXT
);

CREATE TABLE IF NOT EXISTS paoc_auth_transactions (
  transaction_id TEXT PRIMARY KEY,
  client_id TEXT NOT NULL,
  redirect_uri TEXT NOT NULL,
  state TEXT NOT NULL UNIQUE,
  code_challenge TEXT NOT NULL,
  method TEXT NOT NULL,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  consumed_at TEXT
);

CREATE TABLE IF NOT EXISTS paoc_auth_codes (
  code_hash TEXT PRIMARY KEY,
  transaction_id TEXT NOT NULL,
  client_id TEXT NOT NULL,
  redirect_uri TEXT NOT NULL,
  subject TEXT NOT NULL,
  display_name TEXT NOT NULL,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  consumed_at TEXT
);

CREATE TABLE IF NOT EXISTS paoc_ws_tickets (
  ticket_hash TEXT PRIMARY KEY,
  sid TEXT NOT NULL,
  client_id TEXT NOT NULL,
  expert_key TEXT NOT NULL,
  instance_id TEXT NOT NULL,
  origin TEXT NOT NULL,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  consumed_at TEXT
);

CREATE TABLE IF NOT EXISTS paoc_operation_receipts (
  receipt_id TEXT PRIMARY KEY,
  account_partition TEXT NOT NULL,
  source_instance_id TEXT NOT NULL,
  client_id TEXT NOT NULL,
  operation TEXT NOT NULL,
  resource_identity TEXT NOT NULL,
  request_id TEXT NOT NULL,
  request_hash TEXT NOT NULL,
  status_code INTEGER NOT NULL,
  response_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  UNIQUE(account_partition, source_instance_id, client_id, operation, resource_identity, request_id)
);

CREATE TABLE IF NOT EXISTS paoc_personal_bindings (
  binding_id TEXT PRIMARY KEY,
  hub_instance_id TEXT NOT NULL,
  hub_subject TEXT NOT NULL,
  connection_id TEXT NOT NULL,
  peer_instance_id TEXT NOT NULL,
  peer_subject TEXT NOT NULL,
  binding_revision INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  invalidated_at TEXT,
  UNIQUE(hub_instance_id, hub_subject, connection_id)
);

CREATE TABLE IF NOT EXISTS paoc_cursor_snapshots (
  snapshot_id TEXT PRIMARY KEY,
  scope TEXT NOT NULL,
  sid TEXT NOT NULL,
  revision TEXT NOT NULL,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS paoc_uploads (
  upload_id TEXT PRIMARY KEY,
  owner_subject TEXT NOT NULL,
  thread_id TEXT NOT NULL,
  expert_key TEXT NOT NULL,
  filename TEXT NOT NULL,
  media_type TEXT NOT NULL,
  bytes INTEGER NOT NULL,
  sha256 TEXT NOT NULL,
  storage_path TEXT NOT NULL,
  state TEXT NOT NULL,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS paoc_thread_metadata (
  thread_id TEXT PRIMARY KEY,
  expert_key TEXT NOT NULL,
  owner_subject TEXT NOT NULL,
  channel_type TEXT NOT NULL,
  title TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  source_kind TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS paoc_message_projection (
  message_id TEXT PRIMARY KEY,
  thread_id TEXT NOT NULL,
  ord INTEGER NOT NULL,
  role TEXT NOT NULL,
  created_at TEXT NOT NULL,
  client_request_id TEXT,
  UNIQUE(thread_id, ord)
);
""",
    ),
    (
        2,
        """
ALTER TABLE paoc_thread_metadata ADD COLUMN history_revision TEXT NOT NULL DEFAULT '0';
ALTER TABLE paoc_thread_metadata ADD COLUMN runtime_revision TEXT NOT NULL DEFAULT '0';
ALTER TABLE paoc_personal_bindings ADD COLUMN peer_identity_key TEXT NOT NULL DEFAULT '';
CREATE UNIQUE INDEX IF NOT EXISTS paoc_peer_active_binding
  ON paoc_personal_bindings(peer_instance_id, peer_subject)
  WHERE invalidated_at IS NULL;
""",
    ),
]
