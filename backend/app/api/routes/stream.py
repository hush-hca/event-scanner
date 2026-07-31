"""Server-sent event endpoint for dashboard event updates."""

import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.api.services import EventPipeline

router = APIRouter(tags=["events"])


def _pipeline(request: Request) -> EventPipeline:
    return request.app.state.event_pipeline  # type: ignore[no-any-return]


@router.get("/events/stream")
async def event_stream(request: Request) -> StreamingResponse:
    """Emit persisted events and poll for new ones using the SSE wire format."""

    pipeline = _pipeline(request)

    async def generate() -> AsyncIterator[str]:
        cursor = 0
        while True:
            if await request.is_disconnected():
                return
            pending = pipeline.events_after(cursor)
            if pending:
                for item in pending:
                    yield f"event: event\ndata: {json.dumps(item.as_json(), ensure_ascii=False)}\n\n"
                cursor += len(pending)
            else:
                yield ": keepalive\n\n"
                await asyncio.sleep(1)

    return StreamingResponse(generate(), media_type="text/event-stream")
