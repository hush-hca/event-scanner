"""Safe Binance-announcement adapter.

Binance's official developer documentation does not currently document a
public endpoint for its support announcements.  This adapter therefore does
not call, scrape, or infer an unsupported endpoint.  It remains deliberately
blocked for live collection while retaining deterministic parsing of a
redacted, simulated fixture for contract and pipeline tests.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.domain.events import NormalizedEvent

BINANCE_DEVELOPER_DOCS_URL = "https://developers.binance.com/en/docs/introduction"
SOURCE_NAME = "binance_announcements"


class SourceStatus(BaseModel):
    """Secret-free availability result for an ingestion source."""

    model_config = ConfigDict(frozen=True)

    source: str
    status: Literal["blocked"]
    reason: str
    documentation_url: str


class BinanceAnnouncementAdapter:
    """Parse simulated announcement records and report live polling as blocked."""

    def __init__(self, now: Callable[[], datetime] | None = None) -> None:
        self._now = now or (lambda: datetime.now(UTC))

    async def fetch(self) -> list[NormalizedEvent]:
        """Return no live events because no supported announcements API exists."""

        return []

    def source_status(self) -> SourceStatus:
        """Explain why this source is unavailable without claiming connectivity."""

        return SourceStatus(
            source=SOURCE_NAME,
            status="blocked",
            reason=(
                "No public Binance support-announcements API is documented in the "
                "official Binance Developer Documentation; live polling is disabled."
            ),
            documentation_url=BINANCE_DEVELOPER_DOCS_URL,
        )

    def parse_fixture(self, payload: Mapping[str, object]) -> list[NormalizedEvent]:
        """Normalize explicitly simulated, redacted fixture records only.

        The fixture schema is intentionally local and is not represented as a
        Binance production API schema.
        """

        if payload.get("fixture_type") != "redacted_simulated_binance_announcement":
            raise ValueError("only redacted simulated Binance fixtures may be parsed")
        records = payload.get("announcements")
        if not isinstance(records, Sequence) or isinstance(records, (str, bytes)):
            raise ValueError("fixture announcements must be a list")

        return [self._normalize_record(record) for record in records]

    def _normalize_record(self, record: object) -> NormalizedEvent:
        if not isinstance(record, Mapping):
            raise ValueError("fixture announcement must be an object")

        announcement_id = self._required_text(record, "announcement_id")
        published_at = self._parse_utc_timestamp(self._required_text(record, "published_at"))
        title = self._required_text(record, "title")
        body = self._required_text(record, "body")
        reference = self._required_text(record, "reference")
        tickers = self._tickers(record.get("tickers"))
        correlation_id = f"{SOURCE_NAME}:{announcement_id}"

        return NormalizedEvent(
            event_id=correlation_id,
            source=SOURCE_NAME,
            source_timestamp=published_at,
            received_timestamp=self._utc_now(),
            raw_payload_reference=reference,
            content=f"{title}\n\n{body}",
            tickers=tickers,
            correlation_id=correlation_id,
        )

    def _utc_now(self) -> datetime:
        value = self._now()
        if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
            raise ValueError("clock must return a timezone-aware UTC timestamp")
        return value

    @staticmethod
    def _required_text(record: Mapping[str, object], field: str) -> str:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"fixture {field} must be a non-empty string")
        return value

    @staticmethod
    def _parse_utc_timestamp(value: str) -> datetime:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.utcoffset() != UTC.utcoffset(parsed):
            raise ValueError("fixture published_at must be UTC")
        return parsed

    @staticmethod
    def _tickers(value: object) -> tuple[str, ...]:
        if not isinstance(value, list) or not all(isinstance(ticker, str) for ticker in value):
            raise ValueError("fixture tickers must be a list of strings")
        return tuple(value)


def main() -> None:
    """Print the source health state for the operational verification runbook."""

    parser = argparse.ArgumentParser(description="Inspect Binance announcement-source status")
    parser.add_argument("--health", action="store_true", help="print the source health status")
    arguments = parser.parse_args()
    if not arguments.health:
        parser.error("--health is required")
    print(json.dumps(BinanceAnnouncementAdapter().source_status().model_dump(), sort_keys=True))


if __name__ == "__main__":
    main()
