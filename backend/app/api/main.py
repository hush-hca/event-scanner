"""EventRadar HTTP application."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from backend.app.api.routes import events, stream
from backend.app.api.services import EventPipeline
from backend.app.core.config import get_settings
from backend.app.core.logging import configure_logging
from backend.app.worker import run_fixture_once


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize process-wide observability before serving requests."""

    configure_logging()
    settings = get_settings()
    app.state.event_pipeline = EventPipeline(str(settings.development_webhook_url) if settings.development_webhook_url else None)
    # The only current announcement input is a redacted simulated fixture.  Seed
    # it through the production pipeline so the dashboard is observable without
    # misrepresenting it as a live Binance connection.
    run_fixture_once(app.state.event_pipeline)
    yield


app = FastAPI(title="EventRadar API", lifespan=lifespan)
app.include_router(events.router)
app.include_router(stream.router)


@app.get("/")
def index() -> dict[str, str]:
    """Provide a useful deployment-root response instead of a 404."""

    return {
        "service": "EventRadar API",
        "status": "ok",
        "health": "/health",
        "events": "/events",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Return a dependency-free liveness response."""

    return {"status": "ok"}
