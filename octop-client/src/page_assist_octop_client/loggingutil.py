from __future__ import annotations

import json
import logging
import sys
from typing import Any

from page_assist_octop_client.timeutil import rfc3339

FORBIDDEN_KEYS = {"password", "token", "access_token", "code", "ticket", "secret", "authorization"}


class StructuredLogger:
    def __init__(self, level: str = "INFO") -> None:
        self.level = level.upper()
        self._logger = logging.getLogger("page_assist_octop_client")
        self.injections: dict[str, bool] = {}
        self.injection_observed = False
        self.emit_count = 0
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(handler)
        self._logger.setLevel(getattr(logging, self.level, logging.INFO))

    def emit(self, **fields: Any) -> None:
        for key in list(fields):
            if key.lower() in FORBIDDEN_KEYS:
                fields[key] = "[redacted]"
        payload = {
            "timestamp": rfc3339(),
            "level": self.level,
            **fields,
        }
        self.emit_count += 1
        if self.injections.get("fail_logger_write"):
            self.injection_observed = True
            return
        try:
            self._logger.info(json.dumps(payload, ensure_ascii=False))
        except OSError:
            self.injection_observed = True
            return
