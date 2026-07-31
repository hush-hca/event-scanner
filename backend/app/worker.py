"""Fixture-driven P0 worker entry point.

Live Binance announcement polling is deliberately blocked until Binance offers
a documented public endpoint.  This worker provides the same pipeline path for
the redacted fixture used in local verification and E2E tests.
"""

from __future__ import annotations

import json
from pathlib import Path

from backend.app.api.services import EventPipeline
from backend.app.ingestion.binance import BinanceAnnouncementAdapter
from backend.app.routing.service import ProcessedEvent

FIXTURE_PATH = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "binance_announcement.json"


def run_fixture_once(pipeline: EventPipeline, fixture_path: Path = FIXTURE_PATH) -> list[ProcessedEvent]:
    """Process each event in a redacted simulated announcement fixture once."""

    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    events = BinanceAnnouncementAdapter().parse_fixture(payload)
    return [pipeline.process(event) for event in events]
