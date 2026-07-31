"""Transparent, deterministic classification rules for P0 events."""

import re

from backend.app.domain.events import Classification, Direction, EventType, NormalizedEvent, Severity

_TICKER_PATTERN = re.compile(r"(?<![A-Z0-9])\$?([A-Z]{2,10})(?![A-Z0-9])")
_KNOWN_TICKERS = frozenset({"BTC", "ETH", "BNB", "SOL", "XRP", "USDT", "USDC", "DOGE", "ADA", "AVAX"})


def classify(event: NormalizedEvent) -> Classification:
    """Classify an event with stable keyword precedence and no network calls."""

    text = event.content.casefold()
    tickers = event.tickers or _extract_tickers(event.content)

    if _contains(text, "security breach", "hack", "exploit", "compromised", "stolen"):
        return _result("security_incident", "bearish", 4, "critical", 90, tickers)
    if _contains(text, "delist", "delisting", "remove trading pair"):
        return _result("exchange_policy", "bearish", 3, "high", 85, tickers)
    if _contains(text, "list", "listing", "adds trading pair"):
        return _result("exchange_policy", "bullish", 3, "high", 80, tickers)
    if _contains(text, "maintenance", "outage", "service unavailable", "withdrawals suspended"):
        return _result("exchange_technical_outage", "neutral", 3, "medium", 85, tickers)
    if _contains(text, "regulation", "lawsuit", "sec", "legal action"):
        return _result("regulation_legal", "two_sided", 3, "high", 75, tickers)
    if _contains(text, "upgrade", "mainnet", "hard fork", "protocol"):
        return _result("protocol_ecosystem_change", "neutral", 2, "medium", 70, tickers)
    if _contains(text, "whale", "on-chain", "onchain", "large transfer"):
        return _result("onchain_anomaly", "two_sided", 2, "medium", 65, tickers)
    if _contains(text, "influencer", "kol", "ceo said", "statement"):
        return _result("kol_influencer_statement", "neutral", 2, "low", 60, tickers)
    return Classification(ignored=True, tickers=tickers)


def _contains(text: str, *phrases: str) -> bool:
    return any(phrase in text for phrase in phrases)


def _extract_tickers(content: str) -> tuple[str, ...]:
    symbols = (match.group(1) for match in _TICKER_PATTERN.finditer(content))
    return tuple(dict.fromkeys(symbol for symbol in symbols if symbol in _KNOWN_TICKERS))


def _result(
    event_type: EventType,
    direction: Direction,
    volatility: int,
    severity: Severity,
    confidence: int,
    tickers: tuple[str, ...],
) -> Classification:
    return Classification(
        event_type=event_type,
        direction=direction,
        volatility=volatility,
        severity=severity,
        confidence=confidence,
        tickers=tickers,
    )
