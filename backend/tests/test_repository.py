from datetime import UTC, datetime

from app.classification.rules import classify
from app.domain.events import NormalizedEvent
from app.persistence.repository import InMemoryEventRepository, delivery_key


def sample_event() -> NormalizedEvent:
    now = datetime.now(UTC)
    return NormalizedEvent(event_id="announcement-1", source="fixture", source_timestamp=now,
        received_timestamp=now, raw_payload_reference="fixture://announcement-1",
        content="BTC listing", correlation_id="announcement-1")


def test_repository_retains_first_event_and_unique_delivery() -> None:
    repository = InMemoryEventRepository()
    event = sample_event()
    assert repository.store_event(event, classify(event)) is True
    assert repository.store_event(event, classify(event)) is False
    assert repository.reserve_delivery(event.event_id, "development_webhook") is True
    assert repository.reserve_delivery(event.event_id, "development_webhook") is False
    assert delivery_key(event.event_id, "development_webhook") == "announcement-1:development_webhook"
