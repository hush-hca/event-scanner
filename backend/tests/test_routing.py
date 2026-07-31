from app.classification.rules import classify
from app.notifications.webhook import DevelopmentWebhook
from app.persistence.repository import InMemoryEventRepository
from app.routing.service import process_event
from tests.test_repository import sample_event


def test_retry_does_not_send_second_webhook() -> None:
    repository = InMemoryEventRepository()
    webhook = DevelopmentWebhook("http://localhost:9000/webhook")
    event = sample_event()
    process_event(event, classify(event), repository, webhook)
    process_event(event, classify(event), repository, webhook)
    assert webhook.call_count == 1


def test_webhook_is_disabled_without_explicit_url() -> None:
    repository = InMemoryEventRepository()
    webhook = DevelopmentWebhook()
    event = sample_event()
    processed = process_event(event, classify(event), repository, webhook)
    assert processed.deliveries == ()
    assert webhook.call_count == 0
