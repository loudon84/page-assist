from __future__ import annotations

import base64
import hashlib
import secrets

from page_assist_octop_client.constants import TOKEN_PREFIX


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def new_token(prefix: str = TOKEN_PREFIX, nbytes: int = 32) -> str:
    return prefix + _b64url(secrets.token_bytes(nbytes))


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def token_hash(token: str) -> str:
    return hash_secret(token)


def pkce_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return _b64url(digest)
