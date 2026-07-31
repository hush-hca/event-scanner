from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.domain.events import NormalizedEvent


def test_normalized_event_accepts_complete_utc_contract() -> None:
    event = NormalizedEvent(
        event_id="binance:announcement:123",
        source="binance_announcements",
        source_timestamp=datetime(2026, 7, 31, 1, tzinfo=UTC),
        received_timestamp=datetime(2026, 7, 31, 1, 1, tzinfo=UTC),
        raw_payload_reference="binance-announcement:123",
        content="Binance will list $BTC.",
        tickers=["btc", "BTC"],
        correlation_id="binance:123",
    )

    assert event.tickers == ("BTC",)
    assert event.source_timestamp.tzinfo is UTC


def test_normalized_event_rejects_naive_timestamps() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        NormalizedEvent(
            event_id="event-1",
            source="fixture",
            source_timestamp=datetime(2026, 7, 31, 1),
            received_timestamp=datetime(2026, 7, 31, 1, tzinfo=UTC),
            raw_payload_reference="fixture:1",
            content="Example event",
            correlation_id="fixture:1",
        )
