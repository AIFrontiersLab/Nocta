from __future__ import annotations

from collections import defaultdict
from itertools import combinations

from app.llm.schemas import ConvergenceDraft
from app.utils.ids import new_id

TECH_LEXICON = {
    "Voice AI": ["voice", "speech", "audio agent"],
    "Computer Use": ["computer use", "browser agent", "gui agent", "operator"],
    "Agent Identity": ["agent identity", "did", "attestation", "agent auth"],
    "Stablecoins": ["stablecoin", "usdc", "machine payment", "x402"],
    "Robotics": ["robot", "humanoid", "actuator"],
    "Persistent Memory": ["persistent memory", "long-term memory", "world model"],
    "World Models": ["world model", "simulation", "digital twin"],
    "Small Models": ["small model", "on-device", "slm", "local llm"],
    "Smart Glasses": ["glasses", "wearable", "hud"],
    "Agent Commerce": ["agent commerce", "a2a", "agent payment", "autonomous purchase"],
    "Legacy Enterprise": ["sap", "mainframe", "legacy", "oracle forms"],
    "Authorization": ["authorization", "policy", "capability", "permissions"],
    "Reputation": ["reputation", "trust graph", "rating"],
}


def tag_technologies(text: str) -> list[str]:
    blob = (text or "").lower()
    hits = []
    for name, needles in TECH_LEXICON.items():
        if any(n in blob for n in needles):
            hits.append(name)
    return hits


def detect_convergences(signals: list[dict], *, min_strength: float = 5.0) -> list[dict]:
    tech_to_signals: dict[str, list[dict]] = defaultdict(list)
    for sig in signals:
        techs = sig.get("technologies") or tag_technologies(
            " ".join([sig.get("title") or "", sig.get("summary") or "", " ".join(sig.get("tags") or [])])
        )
        sig["technologies"] = techs
        for tech in techs:
            tech_to_signals[tech].append(sig)

    drafts: list[dict] = []
    techs = sorted(tech_to_signals)
    for a, b in combinations(techs, 2):
        shared = {s["id"] for s in tech_to_signals[a]} & {s["id"] for s in tech_to_signals[b]}
        strength = 4 + min(6, len(tech_to_signals[a]) + len(tech_to_signals[b])) / 2
        if shared:
            strength += 1.5
        if strength < min_strength:
            continue
        title = f"{a} × {b}"
        drafts.append(
            {
                "id": new_id("cvg"),
                "title": title,
                "thesis": f"{a} and {b} are appearing in overlapping research and product activity.",
                "nodes": [a, b],
                "why_connect": f"Independent signals mention both {a} and {b}; their joint capability is not yet a named product category.",
                "consequences": [
                    f"Products that assume {a} without {b} will feel incomplete.",
                    f"Infrastructure for {a}+{b} may become a missing primitive.",
                ],
                "opportunities": [f"A product that only exists because {a} and {b} now work together."],
                "signal_ids": list({s["id"] for s in tech_to_signals[a] + tech_to_signals[b]})[:12],
                "strength": round(min(10.0, strength), 1),
            }
        )

    # Prefer surprising triples when three techs co-occur.
    if len(techs) >= 3:
        for a, b, c in list(combinations(techs, 3))[:8]:
            drafts.append(
                {
                    "id": new_id("cvg"),
                    "title": f"{a} × {b} × {c}",
                    "thesis": f"A three-way collision: {a}, {b}, and {c}.",
                    "nodes": [a, b, c],
                    "why_connect": "These capabilities rarely sat in the same stack until recently.",
                    "consequences": ["New product surfaces that none of the three categories own today."],
                    "opportunities": [f"Invent the category that sits at {a} + {b} + {c}."],
                    "signal_ids": list(
                        {s["id"] for s in tech_to_signals[a] + tech_to_signals[b] + tech_to_signals[c]}
                    )[:12],
                    "strength": 7.5,
                }
            )

    drafts.sort(key=lambda d: d["strength"], reverse=True)
    return drafts[:12]


def to_draft(row: dict) -> ConvergenceDraft:
    return ConvergenceDraft.model_validate(row)
