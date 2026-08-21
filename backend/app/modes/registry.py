from __future__ import annotations

from app.modes.implementations import (
    AlienDesignerMode,
    AutoDiscoverMode,
    BackcasterMode,
    FutureProblemMode,
    InternetTelescopeMode,
    InventionLabMode,
    MissingPrimitiveMode,
    ProductEvolutionMode,
    StartupFactoryMode,
    TechnologyCollisionMode,
    WhatComesAfterMode,
)

ALL_MODES = [
    InventionLabMode(),
    FutureProblemMode(),
    TechnologyCollisionMode(),
    MissingPrimitiveMode(),
    BackcasterMode(),
    AlienDesignerMode(),
    WhatComesAfterMode(),
    ProductEvolutionMode(),
    InternetTelescopeMode(),
    StartupFactoryMode(),
    AutoDiscoverMode(),
]

MODE_BY_ID = {m.id: m for m in ALL_MODES}

MODE_ALIASES = {
    "auto-discover": "auto",
    "invention": "invention-lab",
    "autonomous-invention-lab": "invention-lab",
    "future-problems": "future-problem",
    "technology-collision": "technology-collision",
    "collision": "technology-collision",
    "missing-primitive-detector": "missing-primitive",
    "backcaster": "2035-backcaster",
    "alien": "alien-designer",
    "after": "what-comes-after",
    "evolution": "product-evolution",
    "telescope": "internet-telescope",
    "startup-factory": "startup-factory",
    "one-night-startup": "startup-factory",
}


def resolve_mode(mode_id: str):
    key = (mode_id or "auto").strip().lower()
    key = MODE_ALIASES.get(key, key)
    if key not in MODE_BY_ID:
        raise ValueError(f"unknown mode: {mode_id}")
    return MODE_BY_ID[key]


def choose_auto_mode(recent_modes: list[str], signal_blob: str) -> tuple[str, str, str, str]:
    """Pick tonight's experiment. Avoid repeating the same mode unless evidence is strong."""
    blob = (signal_blob or "").lower()
    ranked: list[tuple[str, str, str, str, int]] = []

    def add(mode: str, reason: str, hypothesis: str, theme: str, score: int) -> None:
        penalty = recent_modes[-4:].count(mode) * 3
        ranked.append((mode, reason, hypothesis, theme, score - penalty))

    if any(k in blob for k in ("payment", "escrow", "stablecoin", "commerce", "402")):
        add(
            "missing-primitive",
            "Agent-to-agent commerce signals appeared independently across sources.",
            "Autonomous agents may need transaction trust infrastructure before mass adoption.",
            "Autonomous AI Agents",
            10,
        )
    if any(k in blob for k in ("identity", "auth", "did", "passport")):
        add(
            "missing-primitive",
            "Identity/authorization language is clustering around agents.",
            "The ecosystem is growing faster than its trust primitives.",
            "Autonomous AI Agents",
            9,
        )
    if any(k in blob for k in ("computer use", "operator", "legacy", "rpa", "gui")):
        add(
            "product-evolution",
            "Computer-use + legacy software is an accelerating collision.",
            "The next integration layer may be an agent operator, not an API.",
            "Autonomous AI Agents",
            8,
        )
    if any(k in blob for k in ("world model", "memory", "on-device", "agent memory")):
        add(
            "2035-backcaster",
            "Persistent agent memory / world-model research is heating up.",
            "A 2035 personal agent world model may have a Version 0.1 that is local and private.",
            "Autonomous AI Agents",
            7,
        )
    add(
        "technology-collision",
        "Default: look for surprising AI/agent capability collisions in tonight's signals.",
        "The interesting agentic product sits between categories, not inside one.",
        "Autonomous AI Agents",
        5,
    )
    add(
        "invention-lab",
        "Fallback AI/Agentic invention sweep to avoid mode collapse.",
        "There is still an uninvented useful agentic primitive hiding in the signal set.",
        "Autonomous AI Agents",
        4,
    )
    ranked.sort(key=lambda row: row[4], reverse=True)
    mode, reason, hypothesis, theme, _ = ranked[0]
    return mode, reason, hypothesis, theme
