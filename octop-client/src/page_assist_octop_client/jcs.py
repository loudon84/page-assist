from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_jcs(value: Any) -> str:
    return sha256_hex(canonical_json(value).encode("utf-8"))


def account_partition(
    canonical_origin: str,
    instance_id: str,
    tenant_id: str,
    subject: str,
) -> str:
    return sha256_jcs(
        {
            "v": 1,
            "canonicalOrigin": canonical_origin,
            "instance_id": instance_id,
            "tenant_id": tenant_id,
            "subject": subject,
        }
    )
