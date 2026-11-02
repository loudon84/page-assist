from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from page_assist_octop_client.jcs import sha256_hex, sha256_jcs
from page_assist_octop_client.storage.schema import MIGRATIONS, SCHEMA_CHECKSUM, SCHEMA_VERSION
from page_assist_octop_client.timeutil import rfc3339, parse_rfc3339, utcnow


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = DELETE")
    return conn


class Store:
    def __init__(self, db_path: Path, host: Any | None = None) -> None:
        self.db_path = db_path
        self.host = host
        if host is not None and hasattr(host, "shared_connection"):
            self.conn = host.shared_connection()
            self._owns_connection = False
        else:
            self.conn = connect(db_path)
            self._owns_connection = True
        self._migration_application_count = 0
        self.injections: dict[str, Any] = {}
        self.injection_observed: dict[str, bool] = {}
        self.write_count = 0

    def mark_observed(self, key: str) -> None:
        self.injection_observed[key] = True

    def close(self) -> None:
        if not self._owns_connection:
            return
        try:
            self.conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        except sqlite3.Error:
            pass
        self.conn.close()

    def _before_write(self) -> None:
        if self.injections.get("fail_before_first_write") and self.write_count == 0:
            self.mark_observed("fail_before_first_write")
            raise RuntimeError("injected failure before first write")

    def _after_write(self) -> None:
        self.write_count += 1
        nth = self.injections.get("fail_nth_store_write")
        if nth is not None and self.write_count == int(nth):
            self.mark_observed("fail_nth_store_write")
            raise RuntimeError("injected failure on nth write")
        if self.injections.get("fail_after_first_write") and self.write_count == 1:
            self.mark_observed("fail_after_first_write")
            raise RuntimeError("injected failure after first write")

    @contextmanager
    def txn(self) -> Iterator[sqlite3.Connection]:
        if self.host is not None and getattr(self.host, "_uow_conn", None) is not None:
            if self.injections.get("fail_before_first_write") and self.write_count == 0:
                self.mark_observed("fail_before_first_write")
                raise RuntimeError("injected failure before first write")
            yield self.host._uow_conn
            if self.injections.get("fail_before_commit"):
                self.mark_observed("fail_before_commit")
                raise RuntimeError("injected failure before commit")
            if self.injections.get("fail_after_commit"):
                self.mark_observed("fail_after_commit")
                raise RuntimeError("injected failure after commit")
            return
        if self.injections.get("fail_before_first_write") and self.write_count == 0:
            self.mark_observed("fail_before_first_write")
            raise RuntimeError("injected failure before first write")
        self.conn.execute("BEGIN IMMEDIATE")
        committed = False
        try:
            yield self.conn
            if self.injections.get("fail_before_commit"):
                self.mark_observed("fail_before_commit")
                raise RuntimeError("injected failure before commit")
            self.conn.execute("COMMIT")
            committed = True
            if self.injections.get("fail_after_commit"):
                self.mark_observed("fail_after_commit")
                raise RuntimeError("injected failure after commit")
        except Exception:
            if not committed:
                try:
                    self.conn.execute("ROLLBACK")
                except sqlite3.OperationalError:
                    pass
            raise

    def migrate(self) -> dict[str, Any]:
        existing = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='paoc_schema_version'").fetchone()
        current = 0
        checksum = None
        if existing:
            row = self.conn.execute("SELECT * FROM paoc_schema_version WHERE id=1").fetchone()
            if row:
                current = int(row["version"])
                checksum = str(row["checksum"])
                if current == SCHEMA_VERSION:
                    if checksum != SCHEMA_CHECKSUM:
                        raise RuntimeError("schema checksum conflict")
                    self.conn.execute(
                        "UPDATE paoc_schema_version SET application_count = application_count + 1 WHERE id=1"
                    )
                    self._migration_application_count = int(row["application_count"]) + 1
                    return {
                        "applied": False,
                        "version": SCHEMA_VERSION,
                        "migration_application_count": self._migration_application_count,
                    }
                if current > SCHEMA_VERSION:
                    raise RuntimeError("schema newer than module")
        applied = False
        for index, (version, sql) in enumerate(MIGRATIONS):
            if version <= current:
                continue
            if self.injections.get("fail_during_migrate") and index == 0:
                self.conn.executescript(sql)
                self.mark_observed("fail_during_migrate")
                raise RuntimeError("injected migrate failure")
            self.conn.executescript(sql)
            applied = True
        now = rfc3339()
        self.conn.execute(
            """
            INSERT INTO paoc_schema_version(id, version, checksum, applied_at, reader_min, writer_min, application_count)
            VALUES (1, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(id) DO UPDATE SET version=excluded.version, checksum=excluded.checksum, applied_at=excluded.applied_at, reader_min=excluded.reader_min, writer_min=excluded.writer_min
            """,
            (SCHEMA_VERSION, SCHEMA_CHECKSUM, now, SCHEMA_VERSION, SCHEMA_VERSION),
        )
        self._migration_application_count = 1
        return {
            "applied": applied,
            "version": SCHEMA_VERSION,
            "migration_application_count": 1,
        }

    def count(self, table: str) -> int:
        row = self.conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()
        return int(row["c"]) if row else 0

    def insert_transaction(self, row: dict[str, Any]) -> None:
        self._before_write()
        self.conn.execute(
            """
            INSERT INTO paoc_auth_transactions(
              transaction_id, client_id, redirect_uri, state, code_challenge, method, created_at, expires_at
            ) VALUES (:transaction_id,:client_id,:redirect_uri,:state,:code_challenge,:method,:created_at,:expires_at)
            """,
            row,
        )
        self._after_write()

    def get_transaction_by_state(self, state: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM paoc_auth_transactions WHERE state=?", (state,)
        ).fetchone()
        return dict(row) if row else None

    def get_transaction(self, transaction_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM paoc_auth_transactions WHERE transaction_id=?", (transaction_id,)
        ).fetchone()
        return dict(row) if row else None

    def consume_transaction(self, transaction_id: str, now: str) -> None:
        self.conn.execute(
            "UPDATE paoc_auth_transactions SET consumed_at=? WHERE transaction_id=?",
            (now, transaction_id),
        )

    def insert_code(self, row: dict[str, Any]) -> None:
        self._before_write()
        self.conn.execute(
            """
            INSERT INTO paoc_auth_codes(
              code_hash, transaction_id, client_id, redirect_uri, subject, display_name, created_at, expires_at
            )             VALUES (:code_hash,:transaction_id,:client_id,:redirect_uri,:subject,:display_name,:created_at,:expires_at)
            """,
            row,
        )
        self._after_write()

    def get_code(self, code_hash: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM paoc_auth_codes WHERE code_hash=?", (code_hash,)
        ).fetchone()
        return dict(row) if row else None

    def consume_code(self, code_hash: str, now: str) -> int:
        cur = self.conn.execute(
            "UPDATE paoc_auth_codes SET consumed_at=? WHERE code_hash=? AND consumed_at IS NULL",
            (now, code_hash),
        )
        return cur.rowcount

    def insert_session(self, row: dict[str, Any]) -> None:
        self._before_write()
        self.conn.execute(
            """
            INSERT INTO paoc_sessions(
              sid, token_sha256, instance_id, tenant_id, subject, display_name, client_id, scopes, created_at, expires_at
            ) VALUES (:sid,:token_sha256,:instance_id,:tenant_id,:subject,:display_name,:client_id,:scopes,:created_at,:expires_at)
            """,
            row,
        )
        self._after_write()

    def get_session_by_token_hash(self, token_sha256: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM paoc_sessions WHERE token_sha256=?", (token_sha256,)
        ).fetchone()
        return dict(row) if row else None

    def get_session(self, sid: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM paoc_sessions WHERE sid=?", (sid,)).fetchone()
        return dict(row) if row else None

    def revoke_session(self, sid: str, now: str) -> None:
        self.conn.execute(
            "UPDATE paoc_sessions SET revoked_at=? WHERE sid=?",
            (now, sid),
        )
        self.conn.execute(
            "UPDATE paoc_ws_tickets SET consumed_at=? WHERE sid=? AND consumed_at IS NULL",
            (now, sid),
        )

    def session_count_for_subject(self, subject: str) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM paoc_sessions WHERE subject=?", (subject,)
        ).fetchone()
        return int(row["c"]) if row else 0

    def insert_ticket(self, row: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO paoc_ws_tickets(
              ticket_hash, sid, client_id, expert_key, instance_id, origin, created_at, expires_at
            ) VALUES (:ticket_hash,:sid,:client_id,:expert_key,:instance_id,:origin,:created_at,:expires_at)
            """,
            row,
        )

    def consume_ticket(self, ticket_hash: str, now: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM paoc_ws_tickets WHERE ticket_hash=?", (ticket_hash,)
        ).fetchone()
        if not row:
            return None
        data = dict(row)
        if data["consumed_at"] is not None:
            return {**data, "_replay": True}
        self.conn.execute(
            "UPDATE paoc_ws_tickets SET consumed_at=? WHERE ticket_hash=?",
            (now, ticket_hash),
        )
        return data

    def get_receipt(
        self,
        account_partition: str,
        source_instance_id: str,
        client_id: str,
        operation: str,
        resource_identity: str,
        request_id: str,
    ) -> dict[str, Any] | None:
        row = self.conn.execute(
            """
            SELECT * FROM paoc_operation_receipts
            WHERE account_partition=? AND source_instance_id=? AND client_id=?
              AND operation=? AND resource_identity=? AND request_id=?
            """,
            (account_partition, source_instance_id, client_id, operation, resource_identity, request_id),
        ).fetchone()
        return dict(row) if row else None

    def save_receipt(self, row: dict[str, Any]) -> None:
        if self.injections.get("fail_before_receipt"):
            self.mark_observed("fail_before_receipt")
            raise RuntimeError("injected failure before receipt")
        self._before_write()
        self.conn.execute(
            """
            INSERT INTO paoc_operation_receipts(
              receipt_id, account_partition, source_instance_id, client_id, operation,
              resource_identity, request_id, request_hash, status_code, response_json, created_at, expires_at
            ) VALUES (:receipt_id,:account_partition,:source_instance_id,:client_id,:operation,
              :resource_identity,:request_id,:request_hash,:status_code,:response_json,:created_at,:expires_at)
            """,
            row,
        )
        self._after_write()

    def insert_thread_meta(self, row: dict[str, Any]) -> None:
        self._before_write()
        self.conn.execute(
            """
            INSERT INTO paoc_thread_metadata(
              thread_id, expert_key, owner_subject, channel_type, title, created_at, updated_at, source_kind
            )             VALUES (:thread_id,:expert_key,:owner_subject,:channel_type,:title,:created_at,:updated_at,:source_kind)
            """,
            row,
        )
        self._after_write()

    def get_thread_meta(self, thread_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM paoc_thread_metadata WHERE thread_id=?", (thread_id,)
        ).fetchone()
        return dict(row) if row else None

    def list_thread_meta(self, owner_subject: str, expert_key: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT * FROM paoc_thread_metadata
            WHERE owner_subject=? AND expert_key=?
            ORDER BY updated_at DESC, thread_id ASC
            """,
            (owner_subject, expert_key),
        ).fetchall()
        return [dict(r) for r in rows]

    def insert_upload(self, row: dict[str, Any]) -> None:
        self._before_write()
        self.conn.execute(
            """
            INSERT INTO paoc_uploads(
              upload_id, owner_subject, thread_id, expert_key, filename, media_type, bytes, sha256,
              storage_path, state, created_at, expires_at
            ) VALUES (:upload_id,:owner_subject,:thread_id,:expert_key,:filename,:media_type,:bytes,:sha256,
              :storage_path,:state,:created_at,:expires_at)
            """,
            row,
        )
        self._after_write()

    def get_upload(self, upload_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM paoc_uploads WHERE upload_id=?", (upload_id,)
        ).fetchone()
        return dict(row) if row else None

    def mark_upload_attached(self, upload_id: str) -> None:
        self.conn.execute(
            "UPDATE paoc_uploads SET state='attached' WHERE upload_id=?", (upload_id,)
        )

    def expire_ready_uploads(self, now: str) -> list[str]:
        rows = self.conn.execute(
            """
            SELECT upload_id FROM paoc_uploads
            WHERE state='ready' AND expires_at < ?
            """,
            (now,),
        ).fetchall()
        ids = [r["upload_id"] for r in rows]
        if ids:
            self.conn.execute(
                "UPDATE paoc_uploads SET state='expired' WHERE state='ready' AND expires_at < ?",
                (now,),
            )
        return ids

    def insert_projection(self, row: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO paoc_message_projection(
              message_id, thread_id, ord, role, created_at, client_request_id
            ) VALUES (:message_id,:thread_id,:ord,:role,:created_at,:client_request_id)
            """,
            row,
        )

    def upsert_binding(self, row: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO paoc_personal_bindings(
              binding_id, hub_instance_id, hub_subject, connection_id, peer_instance_id, peer_subject,
              binding_revision, created_at
            ) VALUES (:binding_id,:hub_instance_id,:hub_subject,:connection_id,:peer_instance_id,:peer_subject,
              :binding_revision,:created_at)
            ON CONFLICT(hub_instance_id, hub_subject, connection_id) DO UPDATE SET
              peer_instance_id=excluded.peer_instance_id,
              peer_subject=excluded.peer_subject,
              binding_revision=excluded.binding_revision
            """,
            row,
        )

    def get_binding(self, hub_instance_id: str, hub_subject: str, connection_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            """
            SELECT * FROM paoc_personal_bindings
            WHERE hub_instance_id=? AND hub_subject=? AND connection_id=? AND invalidated_at IS NULL
            """,
            (hub_instance_id, hub_subject, connection_id),
        ).fetchone()
        return dict(row) if row else None

    def invalidate_binding(self, binding_id: str, now: str) -> None:
        self.conn.execute(
            "UPDATE paoc_personal_bindings SET invalidated_at=? WHERE binding_id=?",
            (now, binding_id),
        )

    def pending_auth_count(self) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM paoc_auth_transactions WHERE consumed_at IS NULL"
        ).fetchone()
        return int(row["c"]) if row else 0

    def insert_cursor_snapshot(self, row: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO paoc_cursor_snapshots(
              snapshot_id, scope, sid, revision, created_at, expires_at
            ) VALUES (:snapshot_id,:scope,:sid,:revision,:created_at,:expires_at)
            """,
            row,
        )

    def get_cursor_snapshot(self, snapshot_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM paoc_cursor_snapshots WHERE snapshot_id=?", (snapshot_id,)
        ).fetchone()
        return dict(row) if row else None

    def find_upload_by_receipt(
        self,
        owner_subject: str,
        thread_id: str,
        request_hash: str,
    ) -> dict[str, Any] | None:
        row = self.conn.execute(
            """
            SELECT u.* FROM paoc_uploads u
            WHERE u.owner_subject=? AND u.thread_id=? AND u.sha256=?
            ORDER BY u.created_at DESC LIMIT 1
            """,
            (owner_subject, thread_id, request_hash),
        ).fetchone()
        return dict(row) if row else None
