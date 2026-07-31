import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from app.ingestion import binance
from app.ingestion.binance import BinanceAnnouncementAdapter


def load_fixture(name: str) -> dict[str, object]:
    path = Path(__file__).parent / "fixtures" / name
    return json.loads(path.read_text(encoding="utf-8"))


def test_fixture_normalizes_to_stable_event() -> None:
    adapter = BinanceAnnouncementAdapter(now=lambda: datetime(2026, 7, 31, 1, tzinfo=UTC))

    event = adapter.parse_fixture(load_fixture("binance_announcement.json"))[0]

    assert event.source == "binance_announcements"
    assert event.event_id == "binance_announcements:redacted-fixture-001"
    assert event.correlation_id == event.event_id
    assert event.tickers == ("BTC",)
    assert event.received_timestamp == datetime(2026, 7, 31, 1, tzinfo=UTC)
    assert event.raw_payload_reference.startswith("fixture://")


def test_fetch_is_disabled_without_documented_announcement_endpoint() -> None:
    adapter = BinanceAnnouncementAdapter()

    assert asyncio.run(adapter.fetch()) == []


def test_source_status_reports_blocked_and_official_documentation() -> None:
    status = BinanceAnnouncementAdapter().source_status()

    assert status.source == "binance_announcements"
    assert status.status == "blocked"
    assert "No public Binance support-announcements API is documented" in status.reason
    assert status.documentation_url == "https://developers.binance.com/en/docs/introduction"


def test_fixture_parser_rejects_non_fixture_payload() -> None:
    with pytest.raises(ValueError, match="only redacted simulated"):
        BinanceAnnouncementAdapter().parse_fixture({"announcements": []})


def test_health_cli_reports_blocked_status(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("sys.argv", ["binance", "--health"]):
        binance.main()

    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "blocked"
