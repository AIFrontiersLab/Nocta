from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config.settings import Settings, get_settings


def normalize_whatsapp_target(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        return ""
    if value.lower().startswith("whatsapp:"):
        return value
    return f"whatsapp:{value}"


def whatsapp_target_from_settings(settings: Settings | None = None) -> str:
    s = settings or get_settings()
    return normalize_whatsapp_target(s.hermes_whatsapp_group)


def whatsapp_delivery_enabled(settings: Settings | None = None) -> bool:
    s = settings or get_settings()
    return bool(
        s.hermes_enabled
        and s.nocta_send_whatsapp
        and whatsapp_target_from_settings(s)
    )


def validate_media_path(path: str | Path | None) -> str | None:
    if path is None:
        return None
    resolved = Path(path).expanduser()
    if not resolved.is_absolute():
        raise ValueError(f"media path must be absolute: {path}")
    if not resolved.is_file():
        raise ValueError(f"media file does not exist: {resolved}")
    name = resolved.name.lower()
    blocked = {".env", ".pem", ".key", ".p12", ".pfx", ".crt"}
    if resolved.suffix.lower() in blocked or name in {".env", "credentials.json", "secrets.json"}:
        raise ValueError(f"media path is not allowed: {resolved}")
    return str(resolved)


def delivery_request(
    target: str,
    *,
    message: str | None = None,
    media: str | Path | None = None,
) -> dict[str, Any]:
    validated_media = validate_media_path(media) if media else None
    return {
        "target": target,
        "message": message,
        "media": validated_media,
    }


def build_production_result(
    *,
    status: str,
    message: str,
    deliveries: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "message": message,
        "deliveries": list(deliveries or []),
    }


def success_result(
    message: str = "project execution completed",
    deliveries: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return build_production_result(status="ok", message=message, deliveries=deliveries)


def error_result(message: str) -> dict[str, Any]:
    return build_production_result(status="error", message=message, deliveries=[])
