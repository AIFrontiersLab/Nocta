from app.llm.schemas import DimensionScore
from app.scoring.engine import band_for_score, compute_scorecard
from app.scoring.obvious import is_obvious
from app.utils.similarity import idea_similarity


def test_band_thresholds():
    assert band_for_score(55) == "archive"
    assert band_for_score(65) == "interesting"
    assert band_for_score(75) == "watch"
    assert band_for_score(85) == "prototype_candidate"
    assert band_for_score(92) == "exceptional"


def test_compute_scorecard_caps_weak_why_now():
    dims = {
        key: DimensionScore(score=8, reason="ok", evidence=["x"], confidence=0.7)
        for key in [
            "novelty",
            "problem_severity",
            "market_potential",
            "why_now",
            "technical_feasibility",
            "competitive_white_space",
            "defensibility",
            "distribution_potential",
            "revenue_potential",
            "wow_factor",
            "prototypeability",
            "signal_confidence",
        ]
    }
    dims["why_now"] = DimensionScore(score=3, reason="weak", evidence=[], confidence=0.4)
    card = compute_scorecard(dims)
    assert card.weighted_total <= 72


def test_obvious_filter_rejects_chatbot():
    hit, _ = is_obvious("Another AI chatbot for meetings")
    assert hit


def test_idea_similarity_detects_duplicates():
    a = "Agent Escrow programmable trust layer for autonomous commerce"
    b = "Agent Escrow trust layer for AI-to-AI transactions"
    c = "Personal world model for memory"
    assert idea_similarity(a, b) > 0.7
    assert idea_similarity(a, c) < 0.5
