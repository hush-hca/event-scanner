"""Documented FxTwitter API v2 adapter, restricted to registry entries."""
from datetime import UTC, datetime
from typing import Any
from backend.app.domain.events import NormalizedEvent
from backend.app.ingestion.sources import SourceEntry
BASE_URL = "https://api.fxtwitter.com/2"
class FxTwitterAdapter:
    def parse_response(self, entry: SourceEntry, payload: dict[str, Any]) -> list[NormalizedEvent]:
        if not entry.enabled or payload.get("code") != 200: return []
        events=[]
        for status in payload.get("results", []):
            if not isinstance(status, dict) or status.get("type") != "status": continue
            identifier, text, url = status.get("id"), status.get("text"), status.get("url")
            created = status.get("created_at") or status.get("created_timestamp")
            if not all(isinstance(value, str) and value for value in (identifier, text, url, created)): continue
            timestamp = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if timestamp.tzinfo is None: timestamp = timestamp.replace(tzinfo=UTC)
            events.append(NormalizedEvent(event_id=f"fxtwitter:{entry.handle}:{identifier}", source=f"fxtwitter:{entry.handle}", source_timestamp=timestamp.astimezone(UTC), received_timestamp=datetime.now(UTC), raw_payload_reference=url, content=text, correlation_id=f"fxtwitter:{entry.handle}:{identifier}"))
        return events
