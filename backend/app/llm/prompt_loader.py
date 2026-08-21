from __future__ import annotations

from pathlib import Path

from app.config.settings import Settings, get_settings
from app.utils.logging import get_logger

log = get_logger("prompts")


def load_prompt(name: str, settings: Settings | None = None) -> str:
    s = settings or get_settings()
    path = s.prompts_dir / f"{name}.md"
    if not path.exists():
        # allow nested names like modes/invention_lab or agents/futurist
        path = s.prompts_dir / Path(name + ".md")
    if not path.exists():
        raise FileNotFoundError(f"prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def render_prompt(name: str, **kwargs: str) -> str:
    template = load_prompt(name)
    for key, value in kwargs.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    return template
