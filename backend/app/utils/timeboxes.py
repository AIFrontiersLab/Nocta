from __future__ import annotations

from datetime import datetime, timedelta, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        raw = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def within_last(value: str | datetime | None, *, hours: float) -> bool:
    if value is None:
        return False
    dt = value if isinstance(value, datetime) else parse_iso(str(value))
    if dt is None:
        return False
    return dt >= utc_now() - timedelta(hours=hours)


def night_window(*, hour_start: int = 22, hour_end: int = 6, now: datetime | None = None) -> bool:
    """Return True if local-ish UTC clock is inside the overnight lab window."""
    current = now or utc_now()
    hour = current.hour
    if hour_start <= hour_end:
        return hour_start <= hour < hour_end
    return hour >= hour_start or hour < hour_end
