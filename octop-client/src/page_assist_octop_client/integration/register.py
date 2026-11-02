from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from page_assist_octop_client.api.asgi import ClientApiASGI
from page_assist_octop_client.bridge.personal import BridgeService
from page_assist_octop_client.config import ServerConfig, load_config
from page_assist_octop_client.constants import API_PREFIX
from page_assist_octop_client.errors import ApiError
from page_assist_octop_client.loggingutil import StructuredLogger
from page_assist_octop_client.secrets import ensure_cursor_key
from page_assist_octop_client.storage.db import Store

_REGISTRY: dict[int, "OctopClientModule"] = {}


class OctopClientModule:
    def __init__(self, host: Any, config: ServerConfig) -> None:
        self.host = host
        self.config = config
        self.state = "DISABLED"
        self.ready = False
        self.store: Store | None = None
        self.asgi: ClientApiASGI | None = None
        self.bridge = BridgeService(self)
        self.logger = StructuredLogger(config.log_level)
        self.cursor_key = ensure_cursor_key(config.state_root)
        self.connections: dict[str, Any] = {}
        self.sid_connections: dict[str, set[str]] = {}
        self.revoked_sids: set[str] = set()
        self.closing_sends: list[Any] = []
        self.register_count = 1

    @property
    def enabled_ready(self) -> bool:
        return self.config.enabled and self.ready

    def validate(self) -> None:
        self.state = "VALIDATING"
        if self.host.get_host_api_version() != 1:
            self.state = "FAILED"
            raise ApiError("PROTOCOL_INCOMPATIBLE", "HostPort v1 required", status=426)
        if self.host.worker_count() != 1:
            self.state = "FAILED"
            raise ApiError("CONFIG_INVALID", "B1 requires single worker", status=400)
        if not self.config.enabled:
            self.state = "DISABLED"
            self.ready = False
            return
        if not self.host.is_setup_complete():
            self.state = "FAILED"
            raise ApiError("CLIENT_MODULE_UNAVAILABLE", "host setup incomplete", status=503)

    def start(self) -> None:
        if self.ready:
            return
        if not self.config.enabled:
            self.state = "DISABLED"
            return
        self.state = "REGISTERED"
        db_path = self.host.get_db_path()
        self.host.module = self
        if not self.config.fixture_mode and getattr(self.host, "is_fixture", False):
            self.state = "FAILED"
            raise ApiError("CONFIG_INVALID", "FixtureHostPort is forbidden in production", status=400)
        self.store = Store(db_path, host=self.host)
        self.store.migrate()
        uploads = self.config.state_root / "extensions" / "octop-client" / "uploads"
        uploads.mkdir(parents=True, exist_ok=True)
        self.ready = True
        self.state = "READY"
        self.logger.emit(module="octop-client", phase="activate", result="completed", operation_id="start")

    def stop(self) -> None:
        self.state = "DRAINING"
        self.ready = False
        for send in list(self.connections.values()):
            try:
                pass
            except Exception:
                continue
        self.connections.clear()
        if self.store:
            self.store.close()
        self.state = "STOPPED"

    def register_connection(self, sid: str, connection_id: str, send: Any) -> None:
        self.connections[connection_id] = send
        self.sid_connections.setdefault(sid, set()).add(connection_id)

    def unregister_connection(self, connection_id: str) -> None:
        self.connections.pop(connection_id, None)
        for sid, ids in list(self.sid_connections.items()):
            ids.discard(connection_id)
            if not ids:
                self.sid_connections.pop(sid, None)

    def close_connections(self, sid: str) -> None:
        self.revoked_sids.add(sid)
        for connection_id in list(self.sid_connections.get(sid, set())):
            send = self.connections.pop(connection_id, None)
            if send is not None:
                self.closing_sends.append(send)
        self.sid_connections.pop(sid, None)

    def ws_origin(self) -> str:
        parsed = urlparse(self.config.public_origin)
        return f"wss://{parsed.netloc}"


def register(app: Any, host_port: Any, config: dict[str, Any] | str | Path | ServerConfig) -> OctopClientModule:
    key = id(app) if app is not None else id(host_port)
    existing = _REGISTRY.get(key)
    if existing is not None:
        existing.register_count += 1
        return existing
    if isinstance(config, ServerConfig):
        cfg = config
    else:
        state_root = host_port.get_state_root()
        cfg = load_config(config, state_root=state_root)
        if not cfg.state_root or str(cfg.state_root) in (".", ""):
            cfg.state_root = state_root
    module = OctopClientModule(host_port, cfg)
    try:
        module.validate()
        asgi = ClientApiASGI(module, inner=app)
        module.asgi = asgi
        host_port.mount_client_api(API_PREFIX, asgi)
        host_port.register_auth_bypass(API_PREFIX)
        if cfg.enabled:
            host_port.on_start(module.start)
            host_port.on_stop(module.stop)
            module.start()
        else:
            module.state = "DISABLED"
    except Exception:
        module.state = "FAILED"
        module.ready = False
        raise
    _REGISTRY[key] = module
    return module


def reset_registry() -> None:
    _REGISTRY.clear()
