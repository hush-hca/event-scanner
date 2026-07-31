# Market-Verified Alerts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add reproducible Binance market verification, WATCH/HIGH/CRITICAL scoring, and optional Telegram delivery.

**Architecture:** A public-data adapter holds 60-second symbol observations. Verification derives metrics; scoring persists and routes an enriched alert without any account or trading capability.

**Tech Stack:** Python 3.12, FastAPI, Redis, PostgreSQL, Binance public WebSocket, pytest; Next.js/TypeScript.

## Global Constraints

- Public market data only; never use exchange credentials, accounts, orders, or trading UI.
- Store UTC observations and never log Telegram token/chat ID.
- Live WebSocket claims require a documented health check; fixtures are simulated.

---

### Task 1: Market observation and verification

**Files:** Create `backend/app/verification/binance_market.py`, `backend/app/verification/metrics.py`, `backend/tests/fixtures/binance_market.json`, `backend/tests/test_market_verification.py`.

**Interfaces:** Produce `MarketObservation`, `MarketEvidence`, and `verify(symbol: str, observed_at: datetime) -> MarketEvidence`.

- [ ] **Step 1: Write failing window test.**

```python
def test_verification_measures_price_volume_and_bid_depth():
    evidence = verifier.verify('BTCUSDT', event_time)
    assert evidence.price_change_pct == -4.8
    assert evidence.volume_multiple == 6.1
```

- [ ] **Step 2: Run `cd backend; pytest tests/test_market_verification.py -q`.** Expected: FAIL because verifier is missing.
- [ ] **Step 3: Implement bounded public-stream observation storage and 60-second fixture calculations.**

```python
def verify(self, symbol: str, observed_at: datetime) -> MarketEvidence:
    return self._calculate(self._window(symbol, observed_at, seconds=60))
```

- [ ] **Step 4: Run `cd backend; python -m ruff check .; python -m mypy app; pytest tests/test_market_verification.py -q`.** Expected: PASS.
- [ ] **Step 5: Commit `feat: add Binance market verification`.**

### Task 2: Risk scoring and evidence persistence

**Files:** Create `backend/app/scoring/rules.py`, `backend/app/scoring/models.py`, `backend/tests/test_scoring.py`; modify `backend/app/persistence/models.py`, `backend/app/persistence/repository.py`, `backend/app/routing/service.py`.

**Interfaces:** Consume `Classification`, `MarketEvidence`; produce `RiskAssessment(score: int, tier: Literal['watch','high','critical'], rationale: tuple[str, ...])`.

- [ ] **Step 1: Write failing threshold test.**

```python
def test_critical_requires_independent_evidence_and_market_confirmation():
    assessment = score(trusted_exploit, market_crash, independent_evidence=2)
    assert (assessment.score, assessment.tier) == (92, 'critical')
```

- [ ] **Step 2: Run `cd backend; pytest tests/test_scoring.py -q`.** Expected: FAIL because scorer is missing.
- [ ] **Step 3: Implement score components, strict CRITICAL evidence gate, event evidence audit persistence, and route WATCH dashboard-only.**

```python
if independent_evidence >= 2 and evidence.strong_confirmation:
    tier = 'critical'
elif source_trust >= 60 and evidence.confirmed:
    tier = 'high'
else:
    tier = 'watch'
```

- [ ] **Step 4: Run `cd backend; pytest tests/test_scoring.py tests/test_repository.py tests/test_routing.py -q`.** Expected: PASS.
- [ ] **Step 5: Commit `feat: score market-verified event risk`.**

### Task 3: Telegram, pipeline, and dashboard evidence

**Files:** Create `backend/app/notifications/telegram.py`, `backend/tests/test_telegram.py`; modify `backend/app/core/config.py`, `backend/app/api/services.py`, `backend/app/worker.py`, `backend/tests/test_pipeline_e2e.py`, `web/app/page.tsx`, `web/tests/page.test.tsx`, `README.md`.

**Interfaces:** Consume `RiskAssessment`; produce a secret-safe `TelegramNotifier` and dashboard event including tier, score, rationale, market evidence.

- [ ] **Step 1: Write failing disabled-Telegram and E2E tests.**

```python
def test_missing_credentials_do_not_send_telegram():
    notifier = TelegramNotifier(None, None)
    assert notifier.enabled is False
```

- [ ] **Step 2: Run `cd backend; pytest tests/test_telegram.py tests/test_pipeline_e2e.py -q`.** Expected: FAIL because notifier and enrichment are missing.
- [ ] **Step 3: Implement optional delivery, enriched fixture pipeline, KST evidence display, and configuration documentation.**

```python
enabled = bool(bot_token and chat_id)
```

- [ ] **Step 4: Run `docker compose up -d --build; cd backend; pytest -q; cd ../web; npm run lint; npm run typecheck; npm run test; npm run build`.** Expected: PASS; label unavailable Docker/live WebSocket checks accurately.
- [ ] **Step 5: Commit `feat: deliver market-verified alerts`.**
