from __future__ import annotations

from app.config.settings import Settings, get_settings
from app.llm.schemas import SCORE_DIMENSIONS, DimensionScore, Scorecard

DEFAULT_WEIGHTS = {
    "novelty": 0.12,
    "problem_severity": 0.10,
    "market_potential": 0.08,
    "why_now": 0.12,
    "technical_feasibility": 0.10,
    "competitive_white_space": 0.08,
    "defensibility": 0.07,
    "distribution_potential": 0.06,
    "revenue_potential": 0.07,
    "wow_factor": 0.08,
    "prototypeability": 0.07,
    "signal_confidence": 0.05,
}


def band_for_score(total: float, settings: Settings | None = None) -> str:
    s = settings or get_settings()
    if total < s.score_archive_below:
        return "archive"
    if total < s.score_interesting_below:
        return "interesting"
    if total < s.score_watch_below:
        return "watch"
    if total < s.score_prototype_below:
        return "prototype_candidate"
    return "exceptional"


def recommendation_for_band(band: str) -> str:
    return {
        "exceptional": "BUILD",
        "prototype_candidate": "BUILD",
        "watch": "WATCH",
        "interesting": "RESEARCH",
        "archive": "ARCHIVE",
    }.get(band, "WATCH")


def compute_scorecard(
    dimensions: dict[str, DimensionScore | dict],
    *,
    settings: Settings | None = None,
    extra_reason: str = "",
) -> Scorecard:
    """Weighted total is computed in code. LLMs may propose dimension scores, never the final number."""
    s = settings or get_settings()
    weights = s.score_weights
    parsed: dict[str, DimensionScore] = {}
    for key in SCORE_DIMENSIONS:
        raw = dimensions.get(key)
        if isinstance(raw, DimensionScore):
            parsed[key] = raw
        elif isinstance(raw, dict):
            parsed[key] = DimensionScore.model_validate(raw)
        else:
            parsed[key] = DimensionScore(
                score=5,
                reason="Dimension missing from evaluator; defaulted to 5 with low confidence.",
                evidence=[],
                confidence=0.2,
            )
        parsed[key].score = max(0.0, min(10.0, float(parsed[key].score)))

    weighted = 0.0
    confidence_acc = 0.0
    evidence: list[str] = []
    reasons = []
    for key, dim in parsed.items():
        weighted += dim.score * weights.get(key, 0) * 10.0
        confidence_acc += dim.confidence * weights.get(key, 0)
        reasons.append(f"{key}={dim.score:.1f} ({dim.reason})")
        evidence.extend(dim.evidence[:2])

    # A single very weak why-now or novelty caps exceptional scores.
    if parsed["why_now"].score < 5:
        weighted = min(weighted, 72.0)
    if parsed["novelty"].score < 4:
        weighted = min(weighted, 64.0)
    if parsed["technical_feasibility"].score < 3:
        weighted = min(weighted, 58.0)
    if parsed["signal_confidence"].score < 3:
        weighted = min(weighted, 70.0)

    total = round(max(0.0, min(100.0, weighted)), 1)
    band = band_for_score(total, s)
    reason = extra_reason or "; ".join(reasons[:4])
    return Scorecard(
        dimensions=parsed,
        weighted_total=total,
        band=band,
        reason=reason,
        evidence=evidence[:8],
        confidence=round(max(0.15, min(0.95, confidence_acc)), 2),
    )
