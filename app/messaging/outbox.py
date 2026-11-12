import uuid
from sqlalchemy import select

from app.db import SessionLocal
from app.models import OutboxEvent
from app.messaging.broker import publish


def enqueue(topic: str, payload: dict, idempotency_key: str | None = None) -> uuid.UUID:
    key = idempotency_key or str(uuid.uuid4())
    with SessionLocal() as session:
        event = OutboxEvent(topic=topic, payload=payload, idempotency_key=key)
        session.add(event)
        session.commit()
        return event.id


async def publish_pending(limit: int = 100) -> int:
    published_count = 0
    with SessionLocal() as session:
        events = session.scalars(
            select(OutboxEvent).where(OutboxEvent.published.is_(False)).limit(limit)
        ).all()
        for evt in events:
            try:
                await publish(evt.topic, evt.payload, evt.idempotency_key)
                evt.published = True
                session.commit()
                published_count += 1
            except Exception:
                session.rollback()
                break
    return published_count