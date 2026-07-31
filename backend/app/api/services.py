"""In-process event pipeline state used by the P0 API and worker."""

from __future__ import annotations

from dataclasses import dataclass

from app.classification.rules import classify
from app.domain.events import Classification, NormalizedEvent
from app.notifications.webhook import DevelopmentWebhook
from app.persistence.repository import InMemoryEventRepository
from app.routing.service import ProcessedEvent, process_event


@dataclass(frozen=True)
class DashboardEvent:
    """One persisted event enriched for API and dashboard consumers."""

    event: NormalizedEvent
    classification: Classification

    def as_json(self) -> dict[str, object]:
        """Return JSON-compatible data without exposing webhook configuration."""

        return {
            **self.event.model_dump(mode="json"),
            "classification": self.classification.model_dump(mode="json"),
        }


class EventPipeline:
    """Synchronous processing boundary with a small, ordered SSE event history."""

    def __init__(self, webhook_url: str | None = None) -> None:
        self.repository = InMemoryEventRepository()
        self.webhook = DevelopmentWebhook(webhook_url)
        self._events: list[DashboardEvent] = []

    def process(self, event: NormalizedEvent) -> ProcessedEvent:
        """Classify, persist, route, and publish a new event exactly once."""

        classification = classify(event)
        processed = process_event(event, classification, self.repository, self.webhook)
        if processed.created:
            self._events.append(DashboardEvent(event, classification))
        return processed

    def events_after(self, offset: int = 0) -> list[DashboardEvent]:
        """Return events after an SSE cursor in their original arrival order."""

        return self._events[max(offset, 0) :]

    def all_events(self) -> list[DashboardEvent]:
        """Return newest events first for the dashboard's initial request."""

        return list(reversed(self._events))

    @property
    def event_count(self) -> int:
        return len(self._events)
