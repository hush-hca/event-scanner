"""SQLAlchemy tables for event and delivery audit records."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class shared by all persistence tables."""


class EventRecord(Base):
    """The first observed copy of a source event and its classified payload."""

    __tablename__ = "events"

    event_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DeliveryRecord(Base):
    """An idempotency and audit record for an attempted notification."""

    __tablename__ = "deliveries"
    __table_args__ = (UniqueConstraint("delivery_key", name="uq_deliveries_delivery_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(ForeignKey("events.event_id"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(64), nullable=False)
    delivery_key: Mapped[str] = mapped_column(String(384), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
