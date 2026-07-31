# FxTwitter Allowlist Ingestion Design

## Scope

Add a keyless FxTwitter API v2 source for explicitly allowed X accounts, with user-managed account metadata and dashboard source status. The adapter requests only configured handles, converts returned posts to `NormalizedEvent`, and never performs unrestricted X search or account discovery.

## Default Sources

Exchange/infrastructure: `binance`, `BinanceFutures`, `coinbase`, `Bybit_Official`, `okx`. Security: `certikalert`, `peckshield`, `SlowMist_Team`, `zachxbt`. Regulation: `SECGov`, `CFTC`. Official exchanges, regulators and user-verified project accounts are high trust; security reporters are medium trust.

## Architecture

The `ingestion/fxtwitter.py` adapter uses `https://api.fxtwitter.com/2/`, treats response `code` as authoritative, applies a bounded polling schedule below the documented 1000 requests/minute/IP rate limit, and backs off on failures. Allowlist entries have handle, label, category, trust level and enabled status. The Sources UI reads and updates those entries through FastAPI. The first implementation uses a clearly labelled local development store; PostgreSQL persistence is a required follow-up before claiming multi-instance durability.

## Safety and Verification

No API key is used or stored. Fixtures are redacted and tests distinguish the recorded contract fixture from live health. Each resulting event carries source timestamp, source URL, text, author handle, correlation ID and source trust metadata. Tests cover disabled entries, only-allowlisted polling, API response normalization, malformed response handling and UI source management.
