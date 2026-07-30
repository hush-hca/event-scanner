# EventRadar P0 Design

## Scope

Build the P0 vertical slice of a read-only crypto event scanner. The first real source is a publicly accessible Binance official announcement endpoint. The slice ingests an announcement, normalizes and classifies it, deduplicates it, persists it, routes an idempotent development webhook alert, and displays it live in a Korean dashboard. No trading, account access, order handling, or write-capable exchange credentials are included.

## Architecture

Docker Compose runs five services: a FastAPI API, a FastAPI worker, PostgreSQL, Redis, and a Next.js web application. Backend modules are isolated by bounded context:

- `ingestion`: Binance adapter, poll scheduling, source health and backoff.
- `normalization`: source records to the common `NormalizedEvent` contract.
- `classification`: ticker extraction, allowed event type, direction, volatility, confidence and severity rules.
- `routing`: deduplication, idempotency, severity-to-channel routing.
- `notifications`: development webhook delivery; Telegram/Discord adapters activate only when their environment variables exist.
- `api`: health, event read APIs, and SSE/WebSocket event updates.
- `web`: Korean Next.js dashboard with KST display.

The worker writes event and delivery audit records to PostgreSQL, then publishes dashboard updates through Redis Pub/Sub. The API exposes persisted events and relays updates to the web client.

## Contracts

Every normalized event contains a stable `event_id`, `source`, source timestamp, received timestamp, safe raw payload reference, content, related tickers, event type, direction, volatility (1-4), severity, confidence, and correlation ID. Timestamps are stored in UTC; the UI renders KST.

Allowed event types are security incident, exchange policy, protocol/ecosystem change, KOL/influencer statement, on-chain anomaly, regulation/legal, and exchange technical outage. Directions are `bullish`, `bearish`, `neutral`, and `two_sided`. Volatility maps exactly from `low=1` through `critical=4`.

Duplicate source content retains its first event record. A deterministic delivery key prevents retransmission on retries. Critical routes to all configured channels, high to Telegram and configured push, medium to Telegram, and low remains dashboard-only. In the initial local environment, only the explicitly configured development webhook is delivered; production integrations remain disabled without their environment variables.

## Source Integration

The Binance adapter documents the official endpoint, unauthenticated public access, polling interval/rate limit behavior, reconnect strategy, and a redacted recorded-payload fixture. It uses exponential-backoff retries for recoverable failures and structured JSON logs that exclude secrets and raw credentials. If the public endpoint changes or is unavailable, the source reports degraded status and the fixture supports development testing; that does not claim a live integration.

## Error Handling and Security

Configuration is environment-only with `.env.example` containing variable names but no values. Health endpoints distinguish service health from source readiness. Validation errors, rate limits, and delivery failures are recorded as structured, secret-safe operational events. No credential is logged, persisted in fixtures, or sent to the browser.

## Verification

Focused tests cover normalization, classification, severity routing, deduplication, idempotent deliveries, source contract fixtures, and API/dashboard behavior. An E2E test injects the documented Binance-shaped fixture through the same worker pipeline and verifies persistence, development webhook delivery, and dashboard update. Completion runs Docker Compose, Ruff, mypy, pytest, web lint/typecheck/tests/build, plus a source health check. Report actual ingest-to-alert latency only when measured; fixture latency is labelled simulated.

## Acceptance Boundaries

- Complete: one real Binance official-announcement adapter, P0 event pipeline, safe development webhook, and live Korean dashboard.
- Configurable but unverified without credentials: Telegram, Discord, generic webhook/push providers.
- Deferred: X, additional exchanges, Whale Alert/on-chain providers, market/on-chain confirmation, backtesting, portfolio features, and all execution capabilities.
