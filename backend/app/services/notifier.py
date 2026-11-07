from __future__ import annotations

from typing import Any

from app.config.settings import Settings, get_settings
from app.services.delivery import (
    delivery_request,
    whatsapp_delivery_enabled,
    whatsapp_target_from_settings,
)
from app.utils.logging import get_logger

log = get_logger("whatsapp")


class MorningNotifier:
    """Build WhatsApp delivery instructions for the Mac mini Hermes gateway."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def enabled(self) -> bool:
        return whatsapp_delivery_enabled(self.settings)

    def target(self) -> str:
        return whatsapp_target_from_settings(self.settings)

    def build_delivery(self, message: str) -> dict[str, Any] | None:
        if not self.enabled():
            log.stage("WhatsApp delivery disabled; payload written locally only")
            return None
        target = self.target()
        log.stage("WhatsApp delivery queued for remote Hermes gateway", target=target)
        return delivery_request(target, message=message, media=None)

    def collect_deliveries(self, message: str) -> list[dict[str, Any]]:
        delivery = self.build_delivery(message)
        return [delivery] if delivery else []
