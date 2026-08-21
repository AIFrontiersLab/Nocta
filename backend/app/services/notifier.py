from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from app.config.settings import Settings, get_settings
from app.utils.logging import get_logger

log = get_logger("whatsapp")


class MorningNotifier:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def enabled(self) -> bool:
        return bool(
            self.settings.hermes_enabled
            and self.settings.futurelab_send_whatsapp
            and self._target()
            and self._command()
        )

    def _command(self) -> str:
        configured = self.settings.hermes_command or "hermes"
        return shutil.which(configured) or configured

    def _target(self) -> str:
        raw = (self.settings.hermes_whatsapp_group or "").strip()
        if not raw:
            return ""
        if raw.lower().startswith("whatsapp:"):
            return raw
        return f"whatsapp:{raw}"

    def send(self, message: str) -> None:
        if not self.enabled():
            log.stage("WhatsApp delivery disabled; payload written locally only")
            return
        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", prefix="futurelab-brief-", delete=False, encoding="utf-8"
        ) as handle:
            handle.write(message)
            tmp_path = handle.name
        try:
            cmd = [self._command(), "send", "--to", self._target(), "--quiet", f"FILE:{tmp_path}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(result.stderr or result.stdout or "hermes send failed")
            log.stage("morning brief sent via existing Hermes WhatsApp integration")
        except Exception as exc:
            log.warning(f"WhatsApp delivery failed: {exc}")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
