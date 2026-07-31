"""Validated contracts shared between source adapters and classifiers."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

EventType = Literal[
    "security_incident",
    "exchange_policy",
    "protocol_ecosystem_change",
    "kol_influencer_statement",
    "onchain_anomaly",
    "regulation_legal",
    "exchange_technical_outage",
]
Direction = Literal["bullish", "bearish", "neutral", "two_sided"]
Severity = Literal["low", "medium", "high", "critical"]


class NormalizedEvent(BaseModel):
    """Source-independent, secret-safe event data stored in UTC.

    Classification fields are optional because adapters emit events before the
    deterministic classifier enriches them.
    """

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    event_id: str = Field(min_length=1, max_length=255)
    source: str = Field(min_length=1, max_length=100)
    source_timestamp: datetime
    received_timestamp: datetime
    raw_payload_reference: str = Field(min_length=1, max_length=1000)
    content: str = Field(min_length=1, max_length=20_000)
    tickers: tuple[str, ...] = ()
    event_type: EventType | None = None
    direction: Direction | None = None
    volatility: int | None = Field(default=None, ge=1, le=4)
    severity: Severity | None = None
    confidence: int | None = Field(default=None, ge=0, le=100)
    correlation_id: str = Field(min_length=1, max_length=255)

    @field_validator("source_timestamp", "received_timestamp")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        """Require timezone-aware UTC instants; storage never uses local time."""

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamps must be timezone-aware")
        if value.utcoffset().total_seconds() != 0:
            raise ValueError("timestamps must be UTC")
        return value

    @field_validator("tickers")
    @classmethod
    def normalize_tickers(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        """Canonicalize symbols while preserving their first-seen order."""

        return tuple(dict.fromkeys(ticker.upper() for ticker in value if ticker.strip()))


class Classification(BaseModel):
    """Deterministic enrichment or an explicit ignored-source decision."""

    model_config = ConfigDict(frozen=True)

    ignored: bool = False
    event_type: EventType | None = None
    direction: Direction | None = None
    volatility: int | None = Field(default=None, ge=1, le=4)
    severity: Severity | None = None
    confidence: int | None = Field(default=None, ge=0, le=100)
    tickers: tuple[str, ...] = ()

    @model_validator(mode="after")
    def require_tags_for_routable_event(self) -> "Classification":
        """Prevent partial classifications from reaching persistence or routing."""

        tags = (self.event_type, self.direction, self.volatility, self.severity, self.confidence)
        if self.ignored and any(tag is not None for tag in tags):
            raise ValueError("ignored classifications cannot include event tags")
        if not self.ignored and any(tag is None for tag in tags):
            raise ValueError("routable classifications require all event tags")
        return self
