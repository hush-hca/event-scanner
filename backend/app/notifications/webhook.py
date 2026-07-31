"""Development-only webhook recorder.

This P0 adapter deliberately does not perform an HTTP request.  It records the
would-be payload, allowing end-to-end testing without sending messages outside
the developer's machine or leaking a configured webhook URL.
"""

from dataclasses import dataclass, field
from typing import Protocol

from app.domain.events import Classification, NormalizedEvent


class Webhook(Protocol):
    enabled: bool

    def deliver(self, event: NormalizedEvent, classification: Classification) -> str: ...


@dataclass
class DevelopmentWebhook:
    """Secret-safe recorder enabled only when a development URL is configured."""

    url: str | None = None
    calls: list[dict[str, object]] = field(default_factory=list)

    @property
    def enabled(self) -> bool:
        return bool(self.url)

    @property
    def call_count(self) -> int:
        return len(self.calls)

    def deliver(self, event: NormalizedEvent, classification: Classification) -> str:
        if not self.enabled:
            return "disabled"
        self.calls.append({
            "event_id": event.event_id,
            "source": event.source,
            "severity": classification.severity,
            "event_type": classification.event_type,
            "tickers": list(classification.tickers),
            "content": event.content,
        })
        return "recorded"
