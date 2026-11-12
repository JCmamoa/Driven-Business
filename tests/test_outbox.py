import pytest

from app.messaging import outbox
from app.models import OutboxEvent


def test_enqueue_creates_event(db_session, monkeypatch):
    monkeypatch.setattr(outbox, "SessionLocal", db_session)

    event_id = outbox.enqueue("triage.queue", {"foo": "bar"}, idempotency_key="test-1")
    assert event_id is not None

    with db_session() as s:
        event = s.get(OutboxEvent, event_id)
        assert event.topic == "triage.queue"
        assert event.payload == {"foo": "bar"}
        assert event.published is False


def test_enqueue_generates_idempotency_key(db_session, monkeypatch):
    monkeypatch.setattr(outbox, "SessionLocal", db_session)

    event_id = outbox.enqueue("x", {"a": 1})
    with db_session() as s:
        event = s.get(OutboxEvent, event_id)
        assert event.idempotency_key


@pytest.mark.asyncio
async def test_publish_pending_marks_published(db_session, monkeypatch):
    monkeypatch.setattr(outbox, "SessionLocal", db_session)

    published = []

    async def fake_publish(topic, payload, key):
        published.append((topic, payload, key))

    monkeypatch.setattr(outbox, "publish", fake_publish)

    outbox.enqueue("triage.queue", {"x": 1}, idempotency_key="k1")
    outbox.enqueue("triage.queue", {"x": 2}, idempotency_key="k2")

    count = await outbox.publish_pending()
    assert count == 2
    assert len(published) == 2

    with db_session() as s:
        assert s.query(OutboxEvent).filter_by(published=False).count() == 0