"""Page Assist OctopClient server module (Client API v1)."""

from __future__ import annotations

__version__ = "1.0.0"
PROTOCOL_MAJOR = 1
PROTOCOL_MINOR = 0
MODULE_NAME = "page-assist-octop-client"

from page_assist_octop_client.integration.register import register

__all__ = [
    "PROTOCOL_MAJOR",
    "PROTOCOL_MINOR",
    "__version__",
    "register",
]
