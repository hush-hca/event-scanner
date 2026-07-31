"""Persist classified events and route safe, idempotent notifications."""

from dataclasses import dataclass

from app.domain.events import Classification, NormalizedEvent
from app.notifications.webhook import Webhook
from app.persistence.repository import DeliveryAudit, EventRepository, delivery_key


def channels_for(classification: Classification, webhook_enabled: bool) -> tuple[str, ...]:
    """Apply P0 routing: low/medium dashboard-only; high/critical may use dev webhook."""

    if not webhook_enabled or classification.ignored:
        return ()
    if classification.severity in {"high", "critical"}:
        return ("development_webhook",)
    return ()


@dataclass(frozen=True)
class ProcessedEvent:
    event_id: str
    created: bool
    deliveries: tuple[DeliveryAudit, ...]


def process_event(
    event: NormalizedEvent,
    classification: Classification,
    repository: EventRepository,
    webhook: Webhook,
) -> ProcessedEvent:
    """Persist once, then deliver each enabled channel once, recording every result."""

    created = repository.store_event(event, classification)
    if classification.ignored:
        return ProcessedEvent(event.event_id, created, ())

    audits: list[DeliveryAudit] = []
    for channel in channels_for(classification, webhook.enabled):
        key = delivery_key(event.event_id, channel)
        if not repository.reserve_delivery(event.event_id, channel):
            continue
        try:
            detail = webhook.deliver(event, classification)
            audit = DeliveryAudit(event.event_id, channel, key, "recorded", detail)
        except Exception as exc:  # delivery failures stay auditable and do not expose a URL
            audit = DeliveryAudit(event.event_id, channel, key, "failed", type(exc).__name__)
        repository.record_delivery(audit)
        audits.append(audit)
    return ProcessedEvent(event.event_id, created, tuple(audits))
