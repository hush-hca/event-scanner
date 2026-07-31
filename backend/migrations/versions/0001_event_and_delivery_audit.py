"""Create EventRadar event and delivery audit tables.

Revision ID: 0001_event_and_delivery_audit
Revises:
Create Date: 2026-07-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_event_and_delivery_audit"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("event_id", sa.String(length=255), primary_key=True),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("source_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("correlation_id", sa.String(length=255), nullable=False),
        sa.Column("severity", sa.String(length=20)),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_events_source", "events", ["source"])
    op.create_index("ix_events_correlation_id", "events", ["correlation_id"])
    op.create_index("ix_events_severity", "events", ["severity"])
    op.create_table(
        "deliveries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(length=255), sa.ForeignKey("events.event_id"), nullable=False),
        sa.Column("channel", sa.String(length=64), nullable=False),
        sa.Column("delivery_key", sa.String(length=384), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("detail", sa.Text()),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("delivery_key", name="uq_deliveries_delivery_key"),
    )
    op.create_index("ix_deliveries_event_id", "deliveries", ["event_id"])


def downgrade() -> None:
    op.drop_index("ix_deliveries_event_id", table_name="deliveries")
    op.drop_table("deliveries")
    op.drop_index("ix_events_severity", table_name="events")
    op.drop_index("ix_events_correlation_id", table_name="events")
    op.drop_index("ix_events_source", table_name="events")
    op.drop_table("events")
