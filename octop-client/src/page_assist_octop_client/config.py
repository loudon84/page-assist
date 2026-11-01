from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from page_assist_octop_client.constants import SESSION_TTL_SECONDS
from page_assist_octop_client.errors import ApiError


@dataclass(frozen=True)
class AllowedClient:
    client_id: str
    extension_origin: str
    redirect_uri: str


@dataclass
class ServerConfig:
    schema_version: int
    enabled: bool
    public_origin: str
    allowed_clients: list[AllowedClient]
    state_root: Path
    host_api_version: int
    worker_count: int
    session_ttl_seconds: int
    log_level: str
    fixture_mode: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    def client_by_id(self, client_id: str) -> AllowedClient | None:
        for item in self.allowed_clients:
            if item.client_id == client_id:
                return item
        return None


def _require(data: dict[str, Any], key: str) -> Any:
    if key not in data:
        raise ApiError("CONFIG_INVALID", f"missing required field {key}", status=400)
    return data[key]


def validate_origin(origin: str) -> str:
    parsed = urlparse(origin)
    if parsed.scheme != "https":
        raise ApiError("INSECURE_ENDPOINT", "public_origin must be HTTPS origin", status=400)
    if parsed.username or parsed.password:
        raise ApiError("CONFIG_INVALID", "public_origin must not contain userinfo", status=400)
    if parsed.query or parsed.fragment:
        raise ApiError("CONFIG_INVALID", "public_origin must not contain query or fragment", status=400)
    if parsed.path not in ("", "/"):
        raise ApiError("CONFIG_INVALID", "public_origin must be origin form (root path)", status=400)
    host = parsed.hostname
    if not host:
        raise ApiError("CONFIG_INVALID", "public_origin host missing", status=400)
    netloc = host.lower()
    if parsed.port and parsed.port not in (443,):
        netloc = f"{netloc}:{parsed.port}"
    return f"https://{netloc}"


def load_config(raw: dict[str, Any] | str | Path, *, state_root: Path | None = None) -> ServerConfig:
    if isinstance(raw, (str, Path)):
        path = Path(raw)
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    else:
        data = dict(raw)
    known = {
        "schema_version",
        "enabled",
        "public_origin",
        "allowed_clients",
        "state_root",
        "host_api_version",
        "worker_count",
        "session_ttl_seconds",
        "log_level",
        "fixture_mode",
    }
    unknown = set(data) - known
    if unknown:
        raise ApiError("CONFIG_INVALID", f"unknown config fields: {sorted(unknown)}", status=400)
    schema_version = int(_require(data, "schema_version"))
    if schema_version != 1:
        raise ApiError("CONFIG_INVALID", "schema_version must be 1", status=400)
    origin = validate_origin(str(_require(data, "public_origin")))
    host_api_version = int(_require(data, "host_api_version"))
    if host_api_version != 1:
        raise ApiError("PROTOCOL_INCOMPATIBLE", "host_api_version must be 1", status=426)
    worker_count = int(_require(data, "worker_count"))
    if worker_count != 1:
        raise ApiError("CONFIG_INVALID", "B1 worker_count must be 1", status=400)
    ttl = int(_require(data, "session_ttl_seconds"))
    if ttl != SESSION_TTL_SECONDS:
        raise ApiError("CONFIG_INVALID", "session_ttl_seconds must be 28800", status=400)
    clients_raw = _require(data, "allowed_clients")
    if not isinstance(clients_raw, list) or not clients_raw:
        raise ApiError("CONFIG_INVALID", "allowed_clients must be a non-empty list", status=400)
    clients: list[AllowedClient] = []
    for item in clients_raw:
        if set(item) - {"client_id", "extension_origin", "redirect_uri"}:
            raise ApiError("CONFIG_INVALID", "allowed_clients entry has unknown fields", status=400)
        if "client_secret" in item:
            raise ApiError("CONFIG_INVALID", "client_secret is forbidden", status=400)
        clients.append(
            AllowedClient(
                client_id=str(item["client_id"]),
                extension_origin=str(item["extension_origin"]),
                redirect_uri=str(item["redirect_uri"]),
            )
        )
    root = Path(str(data.get("state_root") or state_root or "."))
    return ServerConfig(
        schema_version=schema_version,
        enabled=bool(_require(data, "enabled")),
        public_origin=origin,
        allowed_clients=clients,
        state_root=root,
        host_api_version=host_api_version,
        worker_count=worker_count,
        session_ttl_seconds=ttl,
        log_level=str(_require(data, "log_level")),
        fixture_mode=bool(data.get("fixture_mode", False)),
    )
