from app.modes.registry import choose_auto_mode, resolve_mode


def test_resolve_mode_aliases():
    assert resolve_mode("missing-primitive-detector").id == "missing-primitive"
    assert resolve_mode("collision").id == "technology-collision"


def test_auto_discover_prefers_commerce_signals():
    blob = "agent payments stablecoin commerce checkout machine payable"
    mode, reason, hypothesis, theme = choose_auto_mode([], blob)
    assert mode == "missing-primitive"
    assert "commerce" in reason.lower() or "agent" in reason.lower()
    assert theme
