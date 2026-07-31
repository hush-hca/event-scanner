# Market-Verified Alerts Design

## Scope

Extend EventRadar from announcement classification to an alert-only, market-verified risk scanner. The first expansion adds Binance public market-data verification, deterministic 0-100 risk scoring, WATCH/HIGH/CRITICAL tiers, event evidence persistence, and optional Telegram delivery. Trading, account access, and order execution remain excluded.

## Architecture

Add `verification` and `scoring` backend contexts after classification. A public Binance WebSocket adapter maintains bounded, in-memory per-symbol observations for price, volume, bid depth, open interest, and funding. When a classified event arrives, verification calculates pre/post-event changes over a 60-second window. Scoring combines source trust, direct asset exposure, market reaction, and derivatives vulnerability into a reproducible score and tier.

Each score persists its input values, observation timestamps, rule version, tier, and rationale with the event. The dashboard renders the tier and evidence. The pipeline publishes the enriched record through the existing event stream.

## Source and Evidence Policy

Initial source trust comes from a project-specific allowlist. Official project, audit, and regulator sources are high trust; verified security researchers are medium; all other sources are low. This phase does not add X scraping. Existing official-announcement or fixture inputs receive source metadata; future Forta/EVM and official channels must emit the same normalized contract.

CRITICAL requires at least two independent evidence classes and strong market or derivatives confirmation. HIGH requires a trusted source or on-chain evidence plus initial market confirmation. WATCH records all remaining credible events in the dashboard without Telegram delivery.

## Notifications and Security

Telegram sends only when both `EVENTRADAR_TELEGRAM_BOT_TOKEN` and `EVENTRADAR_TELEGRAM_CHAT_ID` are set. It includes tier, score, ticker, source, evidence, market and derivative measurements, and a read-only disclaimer. With absent credentials, the development webhook recorder remains the only development delivery target. Tokens and chat IDs are never logged, persisted, serialized to clients, or included in fixtures.

## Verification

Unit tests cover window calculations, score/tier boundaries, independent-evidence requirements, and message redaction. Contract tests use redacted Binance stream fixtures. An E2E fixture passes through normalization, classification, market verification, score, persistence, routing, and dashboard update. Live market connectivity is reported only after a successful public WebSocket health check; fixture results are labeled simulated.

## Deferred

Forta, direct EVM log subscriptions, project source onboarding, multi-exchange verification, historical backtesting, paper trading, and every execution feature are outside this increment.
