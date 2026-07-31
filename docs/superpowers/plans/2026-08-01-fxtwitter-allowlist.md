# FxTwitter Allowlist Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ingest posts only from user-managed, trusted X account allowlists through FxTwitter API v2 and expose them in Sources/dashboard.

**Architecture:** A source registry owns allowlist records. The FxTwitter adapter reads enabled handles, fetches documented API v2 posts below its published limit, normalizes eligible posts and returns health data. FastAPI exposes safe source CRUD; the dashboard manages entries and shows state.

**Tech Stack:** FastAPI/Pydantic/pytest, FxTwitter API v2, Next.js/TypeScript.

## Global Constraints

- Use only configured account handles; never run unrestricted X search or discovery.
- Keep API keys absent; do not log source errors containing sensitive data.
- Mark fixture and failed health results honestly; never call them live data.

---

### Task 1: Registry and FxTwitter contract

**Files:** Create `backend/app/ingestion/sources.py`, `backend/app/ingestion/fxtwitter.py`, `backend/tests/fixtures/fxtwitter_status.json`, `backend/tests/test_fxtwitter.py`.

**Interfaces:** Produces `SourceEntry(handle, label, category, trust, enabled)` and `FxTwitterAdapter.fetch(entry) -> list[NormalizedEvent]`.

- [ ] **Step 1: Write failing allowlist and normalization tests.**

```python
def test_adapter_normalizes_only_enabled_allowlisted_handle():
    events = adapter.parse_response(entry("binance", enabled=True), fixture)
    assert events[0].source == "fxtwitter:binance"
    assert adapter.parse_response(entry("binance", enabled=False), fixture) == []
```

- [ ] **Step 2: Run `cd backend; pytest tests/test_fxtwitter.py -q`.** Expected: FAIL because adapter is missing.
- [ ] **Step 3: Implement default registry, API v2 response validation, stable IDs, source URL references, and documented rate/backoff state.**

```python
async def fetch(self, entry: SourceEntry) -> list[NormalizedEvent]:
    return self.parse_response(entry, await self._get_statuses(entry.handle))
```

- [ ] **Step 4: Run `cd backend; python -m ruff check .; python -m mypy app; pytest tests/test_fxtwitter.py -q`.** Expected: PASS.
- [ ] **Step 5: Commit `feat: add FxTwitter allowlist adapter`.**

### Task 2: Sources API and pipeline integration

**Files:** Create `backend/app/api/routes/sources.py`, `backend/tests/test_sources_api.py`; modify `backend/app/api/main.py`, `backend/app/worker.py`.

**Interfaces:** Produces `GET /sources`, `POST /sources`, `PATCH /sources/{handle}` and an allowlist polling entry point.

- [ ] **Step 1: Write failing source-management test.**

```python
def test_source_api_adds_and_disables_a_handle(client):
    assert client.post('/sources', json={"handle":"projectofficial","label":"Project","category":"project","trust":"high"}).status_code == 201
    assert client.patch('/sources/projectofficial', json={"enabled":False}).json()["enabled"] is False
```

- [ ] **Step 2: Run `cd backend; pytest tests/test_sources_api.py -q`.** Expected: FAIL.
- [ ] **Step 3: Implement validation, duplicate protection, safe status output, and worker polling that calls `pipeline.process`.**

```python
for entry in registry.enabled():
    for event in await adapter.fetch(entry): pipeline.process(event)
```

- [ ] **Step 4: Run `cd backend; pytest tests/test_sources_api.py tests/test_pipeline_e2e.py -q`.** Expected: PASS.
- [ ] **Step 5: Commit `feat: manage allowlisted X sources`.**

### Task 3: Sources dashboard and event provenance

**Files:** Modify `app/page.tsx`, `app/globals.css`; create `app/components/source-manager.tsx` and `app/components/source-manager.test.tsx`.

**Interfaces:** Consumes `/api/sources` and renders source state plus add/disable actions.

- [ ] **Step 1: Write failing component test.**

```tsx
expect(screen.getByText("binance")).toBeInTheDocument();
expect(screen.getByRole("button", { name: "Add source" })).toBeEnabled();
```

- [ ] **Step 2: Run `pnpm run test -- source-manager.test.tsx`.** Expected: FAIL.
- [ ] **Step 3: Implement source table, add form, enabled toggle, trust/category labels, and explicit fixture/live/blocked badges.**

```tsx
await fetch("/api/sources", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(input) })
```

- [ ] **Step 4: Run `pnpm run lint; pnpm run typecheck; pnpm run test; pnpm run build`.** Expected: PASS.
- [ ] **Step 5: Commit `feat: show and manage X source allowlist`.**
