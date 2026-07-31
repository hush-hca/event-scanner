from fastapi.testclient import TestClient

from app.api.main import app
from app.worker import run_fixture_once


def test_fixture_reaches_persistence_webhook_and_stream() -> None:
    with TestClient(app) as client:
        pipeline = app.state.event_pipeline
        pipeline.webhook.url = "http://localhost:9000/webhook"

        processed = run_fixture_once(pipeline)[0]
        response = client.get("/events")

        assert response.status_code == 200
        assert response.json()["items"][0]["event_id"] == processed.event_id
        assert response.json()["items"][0]["classification"]["severity"] == "high"
        assert pipeline.webhook.call_count == 1
        assert pipeline.events_after()[0].event.event_id == processed.event_id
