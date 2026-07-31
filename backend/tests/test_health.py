from fastapi.testclient import TestClient

from app.api.main import app


def test_health_returns_ok() -> None:
    client = TestClient(app)

    assert client.get("/health").json() == {"status": "ok"}
