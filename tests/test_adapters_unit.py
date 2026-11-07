from app.research.adapters.base import SignalRecord
from app.research.adapters import ADAPTERS, default_adapters


def test_signal_record_to_dict():
    record = SignalRecord(
        title="Demo",
        category="research",
        source="unit",
        tags=["agents"],
    )
    payload = record.to_dict()
    assert payload["title"] == "Demo"
    assert payload["tags"] == ["agents"]


def test_default_adapters_registered():
    assert len(ADAPTERS) >= 3
    adapters = default_adapters()
    names = {a.name for a in adapters}
    assert {"github", "hackernews", "papers"} <= names
