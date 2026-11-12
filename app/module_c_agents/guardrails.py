import uuid
from app.config import settings
from app.db import SessionLocal
from app.models import HumanApproval
from app.observability.logging import get_logger

log = get_logger("guardrails")


def requires_human_approval(action: str, amount: float) -> bool:
    if action == "refund" and amount > settings.refund_human_approval_threshold:
        return True
    return False


def create_approval_request(ticket_id: str, action: str, amount: float) -> str:
    with SessionLocal() as session:
        approval = HumanApproval(
            ticket_id=uuid.UUID(ticket_id), action=action, amount=amount
        )
        session.add(approval)
        session.commit()
        log.info("approval_requested", ticket_id=ticket_id, action=action, amount=amount)
        return str(approval.id)


def is_approved(approval_id: str) -> bool:
    with SessionLocal() as session:
        approval = session.get(HumanApproval, uuid.UUID(approval_id))
        return bool(approval and approval.approved)