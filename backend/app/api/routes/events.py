"""REST endpoint for persisted dashboard events."""

from fastapi import APIRouter, Request

from app.api.services import EventPipeline

router = APIRouter(tags=["events"])


def _pipeline(request: Request) -> EventPipeline:
    return request.app.state.event_pipeline  # type: ignore[no-any-return]


@router.get("/events")
def list_events(request: Request) -> dict[str, list[dict[str, object]]]:
    """List classified events newest first; all timestamps remain UTC."""

    return {"items": [item.as_json() for item in _pipeline(request).all_events()]}
