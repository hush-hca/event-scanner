"""EventRadar HTTP application."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from backend.app.api.routes import events, stream
from backend.app.api.services import EventPipeline
from backend.app.core.config import get_settings
from backend.app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize process-wide observability before serving requests."""

    configure_logging()
    settings = get_settings()
    app.state.event_pipeline = EventPipeline(str(settings.development_webhook_url) if settings.development_webhook_url else None)
    yield


app = FastAPI(title="EventRadar API", lifespan=lifespan)
app.include_router(events.router)
app.include_router(stream.router)


@app.get("/health")
def health() -> dict[str, str]:
    """Return a dependency-free liveness response."""

    return {"status": "ok"}
