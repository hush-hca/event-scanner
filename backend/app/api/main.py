"""EventRadar HTTP application."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize process-wide observability before serving requests."""

    configure_logging()
    get_settings()
    yield


app = FastAPI(title="EventRadar API", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    """Return a dependency-free liveness response."""

    return {"status": "ok"}
