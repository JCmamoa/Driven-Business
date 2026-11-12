"""initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

revision = "001"
down_revision = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "outbox_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("topic", sa.String(100), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("idempotency_key", sa.String(200), unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime),
        sa.Column("published", sa.Boolean, default=False),
    )
    op.create_table(
        "processed_messages",
        sa.Column("idempotency_key", sa.String(200), primary_key=True),
        sa.Column("processed_at", sa.DateTime),
    )
    op.create_table(
        "tickets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("external_id", sa.String(100), unique=True),
        sa.Column("channel", sa.String(50)),
        sa.Column("raw_content", sa.Text),
        sa.Column("intent", sa.String(50)),
        sa.Column("urgency", sa.String(20)),
        sa.Column("sentiment", sa.String(20)),
        sa.Column("summary", sa.Text),
        sa.Column("status", sa.String(30)),
        sa.Column("created_at", sa.DateTime),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("sku", sa.String(80), unique=True),
        sa.Column("category", sa.String(80)),
        sa.Column("size", sa.String(20)),
        sa.Column("price", sa.Numeric(10, 2)),
        sa.Column("cost", sa.Numeric(10, 2)),
        sa.Column("logistics_cost", sa.Numeric(10, 2)),
        sa.Column("return_rate", sa.Numeric(5, 4)),
    )
    op.create_table(
        "knowledge_docs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(200)),
        sa.Column("content", sa.Text),
        sa.Column("embedding", Vector(768)),
    )
    op.create_table(
        "agent_traces",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("ticket_id", UUID(as_uuid=True), sa.ForeignKey("tickets.id")),
        sa.Column("step", sa.String(80)),
        sa.Column("payload", sa.JSON),
        sa.Column("created_at", sa.DateTime),
    )
    op.create_table(
        "human_approvals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("ticket_id", UUID(as_uuid=True), sa.ForeignKey("tickets.id")),
        sa.Column("action", sa.String(100)),
        sa.Column("amount", sa.Numeric(10, 2)),
        sa.Column("approved", sa.Boolean, default=False),
        sa.Column("approved_by", sa.String(100)),
        sa.Column("created_at", sa.DateTime),
    )


def downgrade() -> None:
    for t in [
        "human_approvals", "agent_traces", "knowledge_docs",
        "products", "tickets", "processed_messages", "outbox_events",
    ]:
        op.drop_table(t)