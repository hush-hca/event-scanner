# EventRadar P0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable read-only Binance announcement-to-dashboard event scanner.

**Architecture:** Docker Compose runs FastAPI API/worker, PostgreSQL, Redis, and Next.js. The worker normalizes announcements, applies deterministic rules, persists and idempotently routes alerts, then publishes dashboard updates.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy/Alembic, PostgreSQL, Redis, pytest/Ruff/mypy, Next.js, TypeScript, Vitest, Docker Compose.

## Global Constraints

- No trading, exchange-account access, order endpoints, or portfolio UI.
- Store UTC; display KST. Never commit secret values.
- Direction is `bullish`, `bearish`, `neutral`, or `two_sided`; volatility is integer 1–4.
- Binance-specific code stays behind its adapter; fixtures are redacted and clearly simulated.

---

## File Structure

- `docker-compose.yml`, `.env.example`, `README.md`: services, config names, runbook.
- `backend/app/{core,domain,ingestion,classification,persistence,routing,notifications,api}`: bounded backend contexts.
- `backend/tests/`: unit, fixture contract, integration, and E2E coverage.
- `web/`: Korean Next.js dashboard, API/SSE client, UI tests.

### Task 1: Foundation

**Files:** Create `docker-compose.yml`, `.env.example`, `backend/pyproject.toml`, `backend/app/core/config.py`, `backend/app/core/logging.py`, `backend/app/api/main.py`, `backend/tests/test_health.py`, `web/package.json`, `web/app/page.tsx`, `README.md`.

**Interfaces:** Produces `GET /health -> {"status": "ok"}` and environment-only `Settings`.

- [ ] **Step 1: Write the failing health test.**

```python
def test_health_returns_ok(client):
    assert client.get('/health').json() == {'status': 'ok'}
```

- [ ] **Step 2: Run `cd backend; pytest tests/test_health.py -q`.** Expected: FAIL because the API is missing.
- [ ] **Step 3: Implement FastAPI health, JSON logging, configuration validation, Compose services, and Next.js shell.**

```python
@app.get('/health')
def health() -> dict[str, str]: return {'status': 'ok'}
```

- [ ] **Step 4: Run `docker compose up -d --build; cd backend; python -m ruff check .; python -m mypy app; pytest -q; cd ../web; npm run lint; npm run typecheck; npm run build`.** Expected: PASS.
- [ ] **Step 5: Commit `feat: scaffold EventRadar services`.**

### Task 2: Event contract and classification

**Files:** Create `backend/app/domain/events.py`, `backend/app/classification/rules.py`, `backend/tests/test_events.py`, `backend/tests/test_classification.py`.

**Interfaces:** Produces `NormalizedEvent`, `Classification`, `classify(event: NormalizedEvent) -> Classification`.

- [ ] **Step 1: Write the failing security-event classification test.**

```python
def test_security_hack_is_bearish_critical():
    result = classify(make_event('Exchange reports security breach affecting BTC withdrawals'))
    assert (result.event_type, result.direction, result.volatility) == ('security_incident', 'bearish', 4)
```

- [ ] **Step 2: Run `cd backend; pytest tests/test_events.py tests/test_classification.py -q`.** Expected: FAIL.
- [ ] **Step 3: Implement Pydantic contract and deterministic ticker/type/direction/volatility/severity rules.**

```python
def classify(event: NormalizedEvent) -> Classification:
    return Classification(event_type='security_incident', direction='bearish', volatility=4, confidence=90, severity='high')
```

- [ ] **Step 4: Run `cd backend; python -m ruff check app tests; python -m mypy app; pytest tests/test_events.py tests/test_classification.py -q`.** Expected: PASS.
- [ ] **Step 5: Commit `feat: add normalized event classification`.**

### Task 3: Binance source adapter

**Files:** Create `backend/app/ingestion/binance.py`, `backend/tests/fixtures/binance_announcement.json`, `backend/tests/test_binance_adapter.py`.

**Interfaces:** Consumes `NormalizedEvent`; produces `BinanceAnnouncementAdapter.fetch() -> list[NormalizedEvent]` and `source_status()`.

- [ ] **Step 1: Write the failing fixture contract test.**

```python
def test_fixture_normalizes_to_stable_event():
    event = adapter.parse_fixture(load_fixture('binance_announcement.json'))[0]
    assert event.source == 'binance_announcements'
```

- [ ] **Step 2: Run `cd backend; pytest tests/test_binance_adapter.py -q`.** Expected: FAIL.
- [ ] **Step 3: Implement documented public polling, redacted parsing, page bound, retry/backoff, and source status.**

```python
async def fetch(self) -> list[NormalizedEvent]:
    response = await self.client.get(self.endpoint)
    response.raise_for_status()
    return self.parse_payload(response.json())
```

- [ ] **Step 4: Run `cd backend; pytest tests/test_binance_adapter.py -q`.** Expected: PASS; record live health separately, never claim it when unavailable.
- [ ] **Step 5: Commit `feat: add Binance announcement adapter`.**

### Task 4: Persistence, deduplication, and routing

**Files:** Create `backend/app/persistence/{models,repository}.py`, `backend/migrations/`, `backend/app/routing/service.py`, `backend/app/notifications/webhook.py`, `backend/tests/{test_repository,test_routing}.py`.

**Interfaces:** Consumes `NormalizedEvent`, `Classification`; produces `process_event(event) -> ProcessedEvent` with unique event and delivery keys.

- [ ] **Step 1: Write the failing duplicate-webhook test.**

```python
def test_retry_does_not_send_second_webhook(repository, webhook):
    process_event(sample_event(), repository, webhook)
    process_event(sample_event(), repository, webhook)
    assert webhook.call_count == 1
```

- [ ] **Step 2: Run `cd backend; pytest tests/test_repository.py tests/test_routing.py -q`.** Expected: FAIL.
- [ ] **Step 3: Implement migrations, audit records, deduplication, PRD severity routing, and secret-safe webhook messages.**

```python
def delivery_key(event_id: str, channel: str) -> str: return f'{event_id}:{channel}'
```

- [ ] **Step 4: Run `docker compose up -d postgres redis; cd backend; pytest tests/test_repository.py tests/test_routing.py -q`.** Expected: PASS.
- [ ] **Step 5: Commit `feat: persist and route event alerts`.**

### Task 5: Worker, API, SSE, and dashboard

**Files:** Create `backend/app/worker.py`, `backend/app/api/{routes/events,stream}.py`, `backend/tests/test_pipeline_e2e.py`, `web/lib/api.ts`, `web/hooks/use-event-stream.ts`, `web/components/event-table.tsx`, `web/tests/event-table.test.tsx`; modify `backend/app/api/main.py`, `web/app/page.tsx`.

**Interfaces:** Consumes `process_event`; produces `GET /events`, `GET /events/stream`, and Korean/KST event rows.

- [ ] **Step 1: Write failing E2E and UI tests.**

```python
def test_fixture_reaches_persistence_webhook_and_stream(client, webhook):
    processed = run_fixture_once()
    assert client.get('/events').json()['items'][0]['event_id'] == processed.event_id
    assert webhook.call_count == 1
```

```tsx
expect(screen.getByText('이벤트 레이더')).toBeInTheDocument();
```

- [ ] **Step 2: Run `cd backend; pytest tests/test_pipeline_e2e.py -q; cd ../web; npm run test -- event-table.test.tsx`.** Expected: FAIL.
- [ ] **Step 3: Implement pipeline, event API/SSE, and dashboard KST formatting.**

```tsx
new Intl.DateTimeFormat('ko-KR', { timeZone: 'Asia/Seoul', dateStyle: 'short', timeStyle: 'medium' })
```

- [ ] **Step 4: Run `docker compose up -d --build; cd backend; pytest tests/test_pipeline_e2e.py -q; cd ../web; npm run lint; npm run typecheck; npm run test; npm run build`.** Expected: PASS; report fixture latency as simulated.
- [ ] **Step 5: Commit `feat: add live EventRadar dashboard`.**

### Task 6: Completion evidence

**Files:** Modify `README.md`.

**Interfaces:** Produces an acceptance matrix, configuration runbook, and accurately labeled live/fixture verification evidence.

- [ ] **Step 1: Add a PRD acceptance table and required environment variable descriptions.**
- [ ] **Step 2: Run `docker compose up -d --build; cd backend; python -m ruff check .; python -m mypy app; pytest -q; cd ../web; npm run lint; npm run typecheck; npm run test; npm run build`.** Expected: all PASS.
- [ ] **Step 3: Run `cd backend; python -m app.ingestion.binance --health`.** Expected: secret-free source result; label provider/network failure as blocked.
- [ ] **Step 4: Commit `docs: add EventRadar verification runbook`.**
