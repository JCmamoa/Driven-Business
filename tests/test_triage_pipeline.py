import pytest

from app.module_b_triage import pipeline
from app.schemas import TriageResult
from app.models import Ticket, ProcessedMessage


@pytest.fixture()
def fake_triage(monkeypatch):
    async def _fake(subject, body):
        return TriageResult(
            intent="exchange",
            urgency="high",
            sentiment="negative",
            summary_points=["ponto 1", "ponto 2", "ponto 3"],
            suggested_queue="trocas-prioridade",
        )

    monkeypatch.setattr(pipeline, "triage_email", _fake)


@pytest.mark.asyncio
async def test_process_inbound_creates_ticket(db_session, monkeypatch, fake_triage):
    monkeypatch.setattr(pipeline, "SessionLocal", db_session)

    payload = {
        "external_id": "ext-001",
        "channel": "email",
        "subject": "Troca",
        "body": "Quero trocar o produto.",
    }
    await pipeline.process_inbound(payload, idempotency_key="idem-1")

    with db_session() as s:
        ticket = s.query(Ticket).filter_by(external_id="ext-001").one()
        assert ticket.intent == "exchange"
        assert ticket.urgency == "high"
        assert ticket.status == "triaged"
        assert s.get(ProcessedMessage, "idem-1") is not None


@pytest.mark.asyncio
async def test_process_inbound_is_idempotent(db_session, monkeypatch, fake_triage):
    monkeypatch.setattr(pipeline, "SessionLocal", db_session)

    payload = {
        "external_id": "ext-002",
        "channel": "email",
        "subject": "S",
        "body": "B",
    }
    await pipeline.process_inbound(payload, idempotency_key="idem-2")
    await pipeline.process_inbound(payload, idempotency_key="idem-2")

    with db_session() as s:
        assert s.query(Ticket).filter_by(external_id="ext-002").count() == 1