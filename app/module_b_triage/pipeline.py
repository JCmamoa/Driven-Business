from sqlalchemy import select
from app.db import SessionLocal
from app.models import Ticket, ProcessedMessage
from app.module_b_triage.llm_client import triage_email
from app.observability.metrics import TICKETS_TRIAGED


def _already_processed(session, key: str) -> bool:
    return session.get(ProcessedMessage, key) is not None


async def process_inbound(payload: dict, idempotency_key: str) -> None:
    with SessionLocal() as session:
        if _already_processed(session, idempotency_key):
            return

        existing = session.scalar(
            select(Ticket).where(Ticket.external_id == payload["external_id"])
        )
        if existing:
            return

        ticket = Ticket(
            external_id=payload["external_id"],
            channel=payload["channel"],
            raw_content=payload["body"],
        )
        session.add(ticket)
        session.flush()

        result = await triage_email(payload["subject"], payload["body"])

        ticket.intent = result.intent
        ticket.urgency = result.urgency
        ticket.sentiment = result.sentiment
        ticket.summary = " | ".join(result.summary_points)
        ticket.status = "triaged"

        session.add(ProcessedMessage(idempotency_key=idempotency_key))
        session.commit()

        TICKETS_TRIAGED.labels(intent=result.intent).inc()