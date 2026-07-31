"""Fixture-capable verifier for documented Binance public market data."""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

DOCS_URL = "https://developers.binance.com/en/docs/binance-spot-api-docs/web-socket-streams"

@dataclass(frozen=True)
class MarketEvidence:
    price_change_pct: float
    volume_multiple: float
    bid_depth_change_pct: float
    open_interest_change_pct: float
    funding_rate: float

class SourceStatus(BaseModel):
    source: str = "binance_public_market_data"
    status: Literal["not_connected"] = "not_connected"
    documentation_url: str = DOCS_URL

class BinanceMarketVerifier:
    def __init__(self) -> None:
        self._observations: dict[str, list[dict[str, object]]] = {}

    def source_status(self) -> SourceStatus:
        return SourceStatus()

    def load_fixture(self, payload: dict[str, object]) -> None:
        if payload.get("fixture_type") != "simulated_binance_public_market_observations":
            raise ValueError("simulated fixture required")
        for item in payload.get("observations", []):
            if not isinstance(item, dict): raise ValueError("observation must be an object")
            self._observations.setdefault(str(item["symbol"]), []).append(item)

    def verify(self, symbol: str, observed_at: datetime) -> MarketEvidence:
        rows = self._observations.get(symbol, [])
        if len(rows) < 2: raise ValueError("two observations required")
        start, end = rows[0], rows[-1]
        pct = lambda key: round((float(end[key]) / float(start[key]) - 1) * 100, 1)
        return MarketEvidence(pct("price"), round(float(end["volume"])/float(start["volume"]), 1), pct("bid_depth"), pct("open_interest"), float(end["funding_rate"]))
