from datetime import UTC, datetime

from app.classification.rules import classify
from app.domain.events import NormalizedEvent


def make_event(content: str) -> NormalizedEvent:
    return NormalizedEvent(
        event_id="fixture:1",
        source="fixture",
        source_timestamp=datetime(2026, 7, 31, 1, tzinfo=UTC),
        received_timestamp=datetime(2026, 7, 31, 1, 1, tzinfo=UTC),
        raw_payload_reference="fixture:1",
        content=content,
        correlation_id="fixture:1",
    )


def test_security_hack_is_bearish_critical() -> None:
    result = classify(make_event("Exchange reports security breach affecting BTC withdrawals"))

    assert (result.event_type, result.direction, result.volatility) == (
        "security_incident",
        "bearish",
        4,
    )
    assert result.severity == "critical"
    assert result.confidence == 90
    assert result.tickers == ("BTC",)


def test_delisting_takes_precedence_over_listing() -> None:
    result = classify(make_event("Binance will delist BTC and remove the BTC listing."))

    assert (result.event_type, result.direction, result.volatility, result.severity) == (
        "exchange_policy",
        "bearish",
        3,
        "high",
    )


def test_unrecognized_content_is_explicitly_ignored_not_misclassified() -> None:
    result = classify(make_event("Binance publishes a general community update."))

    assert result.ignored is True
    assert result.event_type is None
