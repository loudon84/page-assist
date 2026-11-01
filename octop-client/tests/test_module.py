from __future__ import annotations

import asyncio
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from page_assist_octop_client.auth.tokens import pkce_challenge
from page_assist_octop_client.host.fixture import FixtureHostPort
from page_assist_octop_client.integration.register import register, reset_registry
from page_assist_octop_client.testing import AsgiClient


def cfg(tmp: str) -> dict:
    return {
        "schema_version": 1,
        "enabled": True,
        "public_origin": "https://octop.example.internal",
        "allowed_clients": [
            {
                "client_id": "page-assist-chrome",
                "extension_origin": "chrome-extension://abcdefghijklmnopqrstuvwxyz123456",
                "redirect_uri": "https://abcdefghijklmnopqrstuvwxyz123456.chromiumapp.org/",
            }
        ],
        "state_root": tmp,
        "host_api_version": 1,
        "worker_count": 1,
        "session_ttl_seconds": 28800,
        "log_level": "INFO",
        "fixture_mode": True,
    }


class ModuleTests(unittest.TestCase):
    def test_register_idempotent_and_capabilities(self) -> None:
        asyncio.run(self._run())

    async def _run(self) -> None:
        reset_registry()
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            host = FixtureHostPort(Path(tmp))
            module = register(None, host, cfg(tmp))
            try:
                again = register(None, host, cfg(tmp))
                self.assertIs(module, again)
                self.assertEqual(again.register_count, 2)
                self.assertEqual(len(host.mounted), 1)
                client = AsgiClient(module.asgi)
                status, body = await client.json("GET", "/api/client/v1/capabilities")
                self.assertEqual(status, 200)
                self.assertEqual(body["protocol"]["major"], 1)
                self.assertTrue(body["features"]["independent_threads"])
            finally:
                module.stop()


if __name__ == "__main__":
    unittest.main()
