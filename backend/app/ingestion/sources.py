"""User-managed allowlist for X sources."""
from dataclasses import dataclass, asdict

@dataclass
class SourceEntry:
    handle: str
    label: str
    category: str
    trust: str
    enabled: bool = True
    def as_json(self) -> dict[str, object]: return asdict(self)

DEFAULT_SOURCES = [
    SourceEntry("binance", "Binance", "exchange", "high"), SourceEntry("BinanceFutures", "Binance Futures", "exchange", "high"),
    SourceEntry("coinbase", "Coinbase", "exchange", "high"), SourceEntry("Bybit_Official", "Bybit", "exchange", "high"), SourceEntry("okx", "OKX", "exchange", "high"),
    SourceEntry("certikalert", "CertiK Alert", "security", "medium"), SourceEntry("peckshield", "PeckShield", "security", "medium"),
    SourceEntry("SlowMist_Team", "SlowMist", "security", "medium"), SourceEntry("zachxbt", "ZachXBT", "security", "medium"),
    SourceEntry("SECGov", "SEC", "regulator", "high"), SourceEntry("CFTC", "CFTC", "regulator", "high"),
]
class SourceRegistry:
    def __init__(self) -> None: self._entries = {entry.handle.lower(): entry for entry in DEFAULT_SOURCES}
    def list(self) -> list[SourceEntry]: return list(self._entries.values())
    def add(self, entry: SourceEntry) -> SourceEntry:
        key = entry.handle.lstrip("@").lower()
        if not key or key in self._entries: raise ValueError("handle must be unique")
        entry.handle = entry.handle.lstrip("@")
        self._entries[key] = entry; return entry
    def update(self, handle: str, enabled: bool) -> SourceEntry:
        entry = self._entries[handle.lower()]; entry.enabled = enabled; return entry
