import json
from datetime import UTC, datetime
from pathlib import Path

from app.verification.binance_market import BinanceMarketVerifier


def test_verification_measures_price_volume_and_bid_depth() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "binance_market.json"
    verifier = BinanceMarketVerifier()
    verifier.load_fixture(json.loads(fixture_path.read_text(encoding="utf-8")))
    event_time = datetime(2026, 8, 1, 0, 1, tzinfo=UTC)

    evidence = verifier.verify("BTCUSDT", event_time)

    assert evidence.price_change_pct == -4.8
    assert evidence.volume_multiple == 6.1
    assert evidence.bid_depth_change_pct == -72.0


def test_source_status_is_secret_free_and_references_official_docs() -> None:
    status = BinanceMarketVerifier().source_status()

    assert status.source == "binance_public_market_data"
    assert status.status == "not_connected"
    assert status.documentation_url.startswith("https://developers.binance.com/")
