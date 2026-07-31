"""Repositories that preserve events and make notification retries idempotent."""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock
from typing import Protocol

from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from backend.app.domain.events import Classification, NormalizedEvent
from backend.app.persistence.models import Base, DeliveryRecord, EventRecord


def delivery_key(event_id: str, channel: str) -> str:
    """Return the stable unique key used for one event/channel delivery."""

    return f"{event_id}:{channel}"


@dataclass(frozen=True)
class StoredEvent:
    event: NormalizedEvent
    classification: Classification


@dataclass(frozen=True)
class DeliveryAudit:
    event_id: str
    channel: str
    delivery_key: str
    status: str
    detail: str | None = None


class EventRepository(Protocol):
    def store_event(self, event: NormalizedEvent, classification: Classification) -> bool: ...

    def reserve_delivery(self, event_id: str, channel: str) -> bool: ...

    def record_delivery(self, audit: DeliveryAudit) -> None: ...


class InMemoryEventRepository:
    """Thread-safe repository used by local development and focused tests."""

    def __init__(self) -> None:
        self.events: dict[str, StoredEvent] = {}
        self.deliveries: dict[str, DeliveryAudit] = {}
        self._lock = Lock()

    def store_event(self, event: NormalizedEvent, classification: Classification) -> bool:
        with self._lock:
            if event.event_id in self.events:
                return False
            self.events[event.event_id] = StoredEvent(event, classification)
            return True

    def reserve_delivery(self, event_id: str, channel: str) -> bool:
        key = delivery_key(event_id, channel)
        with self._lock:
            if key in self.deliveries:
                return False
            self.deliveries[key] = DeliveryAudit(event_id, channel, key, "reserved")
            return True

    def record_delivery(self, audit: DeliveryAudit) -> None:
        with self._lock:
            self.deliveries[audit.delivery_key] = audit


class SqlAlchemyEventRepository:
    """PostgreSQL/SQLite repository; unique constraints backstop concurrent workers."""

    def __init__(self, database_url: str) -> None:
        self._engine = create_engine(database_url, future=True)
        self._sessions = sessionmaker(self._engine, expire_on_commit=False)

    def create_schema(self) -> None:
        Base.metadata.create_all(self._engine)

    def store_event(self, event: NormalizedEvent, classification: Classification) -> bool:
        payload = {"event": event.model_dump(mode="json"), "classification": classification.model_dump(mode="json")}
        with self._sessions.begin() as session:
            if session.get(EventRecord, event.event_id) is not None:
                return False
            session.add(EventRecord(
                event_id=event.event_id, source=event.source,
                source_timestamp=event.source_timestamp, received_timestamp=event.received_timestamp,
                correlation_id=event.correlation_id, severity=classification.severity,
                payload_json=json.dumps(payload, separators=(",", ":")), created_at=datetime.now(UTC),
            ))
        return True

    def reserve_delivery(self, event_id: str, channel: str) -> bool:
        key = delivery_key(event_id, channel)
        try:
            with self._sessions.begin() as session:
                session.add(DeliveryRecord(
                    event_id=event_id, channel=channel, delivery_key=key, status="reserved",
                    detail=None, attempted_at=datetime.now(UTC),
                ))
        except IntegrityError:
            return False
        return True

    def record_delivery(self, audit: DeliveryAudit) -> None:
        with self._sessions.begin() as session:
            record = session.scalar(select(DeliveryRecord).where(DeliveryRecord.delivery_key == audit.delivery_key))
            if record is None:
                raise KeyError(f"delivery was not reserved: {audit.delivery_key}")
            record.status = audit.status
            record.detail = audit.detail
            record.attempted_at = datetime.now(UTC)
