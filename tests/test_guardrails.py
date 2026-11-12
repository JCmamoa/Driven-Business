import uuid
import pytest

from app.config import settings
from app.module_c_agents import guardrails


def test_refund_below_threshold_no_approval():
    assert guardrails.requires_human_approval(
        "refund", settings.refund_human_approval_threshold - 1
    ) is False


def test_refund_above_threshold_requires_approval():
    assert guardrails.requires_human_approval(
        "refund", settings.refund_human_approval_threshold + 1
    ) is True


def test_other_actions_never_require_approval():
    assert guardrails.requires_human_approval("exchange", 99999) is False


def test_create_approval_request_persists(db_session, monkeypatch):
    monkeypatch.setattr(guardrails, "SessionLocal", db_session)

    ticket_id = str(uuid.uuid4())
    approval_id = guardrails.create_approval_request(ticket_id, "refund", 500.0)
    assert approval_id is not None

    with db_session() as s:
        from app.models import HumanApproval
        record = s.get(HumanApproval, uuid.UUID(approval_id))
        assert record is not None
        assert record.approved is False
        assert float(record.amount) == 500.0


def test_is_approved_reflects_boolean(db_session, monkeypatch):
    monkeypatch.setattr(guardrails, "SessionLocal", db_session)

    ticket_id = str(uuid.uuid4())
    approval_id = guardrails.create_approval_request(ticket_id, "refund", 500.0)
    assert guardrails.is_approved(approval_id) is False

    with db_session() as s:
        from app.models import HumanApproval
        record = s.get(HumanApproval, uuid.UUID(approval_id))
        record.approved = True
        s.commit()

    assert guardrails.is_approved(approval_id) is True