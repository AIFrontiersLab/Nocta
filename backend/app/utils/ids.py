from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def utc_now_iso() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


def new_id(prefix: str = "id") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"
