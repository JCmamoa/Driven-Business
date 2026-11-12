from fastapi import FastAPI, HTTPException
from app.schemas import InboundEmail
from app.messaging.outbox import enqueue
from app.db import Base, engine
from app.module_b_triage.connectors import WebhookConnector

app = FastAPI(title="AI-Driven Business Ops")


@app.on_event("startup")
def _startup() -> None:
    Base.metadata.create_all(engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/webhooks/zendesk")
def zendesk_webhook(payload: dict) -> dict:
    try:
        email = WebhookConnector.parse_zendesk(payload)
    except KeyError as exc:
        raise HTTPException(400, f"payload inválido: {exc}") from exc

    enqueue(
        "triage.queue",
        email.model_dump(),
        idempotency_key=f"zendesk-{email.external_id}",
    )
    return {"status": "queued", "external_id": email.external_id}


@app.post("/tickets/{ticket_id}/run-agent")
def run_agent_endpoint(ticket_id: str, message: str) -> dict:
    enqueue("agent.queue", {"ticket_id": ticket_id, "message": message})
    return {"status": "queued"}