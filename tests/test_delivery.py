from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.config.settings import Settings, clear_settings_cache
from app.orchestration.result import ExperimentResult
from app.services.delivery import (
    delivery_request,
    error_result,
    success_result,
    validate_media_path,
    whatsapp_target_from_settings,
)
from app.services.notifier import MorningNotifier
from app.services.reporter import whatsapp_payload


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    clear_settings_cache()
    yield
    clear_settings_cache()


def test_whatsapp_target_preserves_group_id():
    settings = Settings(hermes_whatsapp_group="120363012345678901@g.us")
    assert whatsapp_target_from_settings(settings) == "whatsapp:120363012345678901@g.us"


def test_whatsapp_target_preserves_existing_prefix():
    settings = Settings(hermes_whatsapp_group="whatsapp:120363012345678901@g.us")
    assert whatsapp_target_from_settings(settings) == "whatsapp:120363012345678901@g.us"


def test_text_only_delivery_serializes_correctly():
    delivery = delivery_request(
        "whatsapp:120363012345678901@g.us",
        message="Morning brief",
        media=None,
    )
    assert delivery == {
        "target": "whatsapp:120363012345678901@g.us",
        "message": "Morning brief",
        "media": None,
    }


def test_media_only_delivery_serializes_correctly(tmp_path: Path):
    media_file = tmp_path / "poster.png"
    media_file.write_bytes(b"png")
    delivery = delivery_request(
        "whatsapp:120363012345678901@g.us",
        message=None,
        media=media_file,
    )
    assert delivery["message"] is None
    assert delivery["media"] == str(media_file.resolve())


def test_multiple_deliveries_preserve_order():
    deliveries = [
        delivery_request("whatsapp:120363012345678901@g.us", message="First", media=None),
        delivery_request("whatsapp:120363012345678901@g.us", message=None, media=None),
    ]
    payload = success_result(deliveries=deliveries)
    assert payload["deliveries"][0]["message"] == "First"
    assert payload["deliveries"][1]["message"] is None


def test_media_path_must_be_absolute(tmp_path: Path):
    relative = Path("relative.png")
    with pytest.raises(ValueError, match="absolute"):
        validate_media_path(relative)


def test_media_path_must_exist(tmp_path: Path):
    missing = tmp_path / "missing.png"
    with pytest.raises(ValueError, match="does not exist"):
        validate_media_path(missing)


def test_failed_workload_does_not_return_status_ok():
    run = MagicMock()
    run.status = "failed"
    run.error = "signal discovery failed"
    result = ExperimentResult(run=run, deliveries=[])
    payload = result.to_production_dict()
    assert payload["status"] == "error"
    assert payload["deliveries"] == []
    assert payload["message"] == "signal discovery failed"


def test_success_result_always_has_deliveries_array():
    payload = success_result()
    assert payload["status"] == "ok"
    assert payload["deliveries"] == []


def test_error_result_always_has_empty_deliveries():
    payload = error_result("boom")
    assert payload == {"status": "error", "message": "boom", "deliveries": []}


def test_morning_notifier_does_not_execute_hermes_send():
    settings = Settings(
        hermes_enabled=True,
        nocta_send_whatsapp=True,
        hermes_whatsapp_group="120363012345678901@g.us",
    )
    notifier = MorningNotifier(settings)
    with patch("subprocess.run") as mock_run:
        deliveries = notifier.collect_deliveries("Test message")
    mock_run.assert_not_called()
    assert len(deliveries) == 1
    assert deliveries[0]["target"] == "whatsapp:120363012345678901@g.us"
    assert deliveries[0]["message"] == "Test message"
    assert deliveries[0]["media"] is None


def test_morning_notifier_disabled_returns_no_deliveries():
    settings = Settings(
        hermes_enabled=False,
        nocta_send_whatsapp=True,
        hermes_whatsapp_group="120363012345678901@g.us",
    )
    notifier = MorningNotifier(settings)
    assert notifier.collect_deliveries("Test message") == []


def test_whatsapp_payload_generation_unchanged():
    run = MagicMock()
    run.theme = "Agent Commerce"
    run.hypothesis = "Agents will pay each other"
    run.mode = "missing-primitive"
    run.unexpected_insight = "Identity is the missing layer"
    run.recommendation = "WATCH"
    winner = MagicMock()
    winner.name = "Agent Escrow"
    winner.one_liner = "Escrow for autonomous agents"
    winner.score = 82.5
    payload = whatsapp_payload(run, winner, [])
    assert "NOCTA" in payload
    assert "Agent Escrow" in payload
    assert "82/100" in payload


def test_cli_json_output_does_not_execute_hermes_send(capsys):
    from app.cli import main

    completed_run = MagicMock()
    completed_run.status = "completed"
    completed_run.id = "run_test"
    completed_run.winner_id = "idea_test"
    experiment_result = ExperimentResult(
        run=completed_run,
        deliveries=[
            delivery_request(
                "whatsapp:120363012345678901@g.us",
                message="Brief",
                media=None,
            )
        ],
    )

    with patch("app.cli.run_experiment", return_value=experiment_result):
        with patch("app.cli.init_db"):
            with patch("app.cli.ensure_directories"):
                with patch("app.cli.setup_logging"):
                    with patch("app.cli.get_settings", return_value=Settings()):
                        exit_code = main(["run", "--json", "--dry-run"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out.strip())
    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["deliveries"][0]["target"] == "whatsapp:120363012345678901@g.us"
    assert "hermes" not in captured.out.lower()


def test_no_runtime_subprocess_hermes_in_notifier_module():
    notifier_path = Path(__file__).resolve().parents[1] / "backend/app/services/notifier.py"
    source = notifier_path.read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "hermes send" not in source
