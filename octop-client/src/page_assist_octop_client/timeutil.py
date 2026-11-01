from __future__ import annotations

from datetime import datetime, timedelta, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def rfc3339(dt: datetime | None = None) -> str:
    value = dt or utcnow()
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_rfc3339(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def later(seconds: int, dt: datetime | None = None) -> str:
    return rfc3339((dt or utcnow()) + timedelta(seconds=seconds))
