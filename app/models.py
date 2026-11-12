import uuid
from datetime import datetime

from sqlalchemy import String, Text, Numeric, Integer, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.db import Base


class OutboxEvent(Base):
    __tablename__ = "outbox_events"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    published: Mapped[bool] = mapped_column(Boolean, default=False)


class ProcessedMessage(Base):
    __tablename__ = "processed_messages"
    idempotency_key: Mapped[str] = mapped_column(String(200), primary_key=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(100), unique=True)
    channel: Mapped[str] = mapped_column(String(50))
    raw_content: Mapped[str] = mapped_column(Text)
    intent: Mapped[str | None] = mapped_column(String(50))
    urgency: Mapped[str | None] = mapped_column(String(20))
    sentiment: Mapped[str | None] = mapped_column(String(20))
    summary: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(80), unique=True)
    category: Mapped[str] = mapped_column(String(80))
    size: Mapped[str] = mapped_column(String(20))
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    cost: Mapped[float] = mapped_column(Numeric(10, 2))
    logistics_cost: Mapped[float] = mapped_column(Numeric(10, 2))
    return_rate: Mapped[float] = mapped_column(Numeric(5, 4), default=0.0)


class KnowledgeDoc(Base):
    __tablename__ = "knowledge_docs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(768))


class AgentTrace(Base):
    __tablename__ = "agent_traces"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tickets.id"))
    step: Mapped[str] = mapped_column(String(80))
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HumanApproval(Base):
    __tablename__ = "human_approvals"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tickets.id"))
    action: Mapped[str] = mapped_column(String(100))
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)