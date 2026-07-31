"""Documented FxTwitter API v2 adapter, restricted to registry entries."""
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote
from urllib.request import urlopen
from backend.app.domain.events import NormalizedEvent
from backend.app.ingestion.sources import SourceEntry
BASE_URL = "https://api.fxtwitter.com/2"
class FxTwitterAdapter:
    def fetch(self, entry: SourceEntry) -> list[NormalizedEvent]:
        """Read only this allowlisted profile's five newest posts from API v2."""
        if not entry.enabled:
            return []
        url = f"{BASE_URL}/profile/{quote(entry.handle, safe='')}/statuses?count=5"
        try:
            with urlopen(url, timeout=8) as response:  # noqa: S310 - fixed HTTPS host
                import json
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []
        return self.parse_response(entry, payload)
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
