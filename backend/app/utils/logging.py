from __future__ import annotations

import json
import logging
import sys
from typing import Any

from app.config.settings import get_settings


class NoctaLogger:
    PREFIX = "NOCTA"

    def __init__(self, name: str = "nocta") -> None:
        self._logger = logging.getLogger(name)

    def stage(self, message: str, **fields: Any) -> None:
        extras = " ".join(f"{k}={v}" for k, v in fields.items() if v is not None)
        text = f"[{self.PREFIX}] {message}"
        if extras:
            text = f"{text} {extras}"
        self._logger.info(text)

    def event(self, **fields: Any) -> None:
        safe = {k: v for k, v in fields.items() if k.lower() not in {"api_key", "token", "secret", "password"}}
        self._logger.info("[%s] %s", self.PREFIX, json.dumps(safe, default=str))

    def info(self, message: str, *args: Any) -> None:
        self._logger.info(message, *args)

    def warning(self, message: str, *args: Any) -> None:
        self._logger.warning(message, *args)

    def error(self, message: str, *args: Any) -> None:
        self._logger.error(message, *args)

    def exception(self, message: str, *args: Any) -> None:
        self._logger.exception(message, *args)


def setup_logging(level: str | None = None) -> NoctaLogger:
    settings = get_settings()
    log_level = (level or settings.log_level or "INFO").upper()
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%H:%M:%S"))
        root.addHandler(handler)
    root.setLevel(getattr(logging, log_level, logging.INFO))
    return NoctaLogger("nocta")


def get_logger(name: str = "nocta") -> NoctaLogger:
    return NoctaLogger(name)
