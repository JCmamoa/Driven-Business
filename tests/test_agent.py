import uuid
import pytest

from app.module_c_agents import agent
from app.models import Ticket


@pytest.fixture()
def seeded_ticket(db_session, monkeypatch):
    monkeypatch.setattr(agent, "SessionLocal", db_session)
    with db_session() as s:
        t = Ticket(
            external_id="agent-001",
            channel="email",
            raw_content="quero reembolso",
            intent="complaint",
            summary="p1 | p2 | p3",
            status="triaged",
        )
        s.add(t)
        s.commit()
        return str(t.id)


def test_requires_human_approval_threshold(monkeypatch):
    from app.module_c_agents import guardrails
    from app.config import settings

    assert guardrails.requires_human_approval(
        "refund", settings.refund_human_approval_threshold + 0.01
    )


@pytest.mark.asyncio
async def test_agent_missing_ticket_raises(monkeypatch, db_session):
    monkeypatch.setattr(agent, "SessionLocal", db_session)
    with pytest.raises(ValueError):
        await agent.run_agent(str(uuid.uuid4()), "oi")