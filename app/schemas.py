from typing import Literal
from pydantic import BaseModel, Field


Intent = Literal["exchange", "product_question", "tracking", "complaint", "other"]
Urgency = Literal["low", "medium", "high", "critical"]
Sentiment = Literal["positive", "neutral", "negative"]


class TriageResult(BaseModel):
    intent: Intent
    urgency: Urgency
    sentiment: Sentiment
    summary_points: list[str] = Field(min_length=3, max_length=3)
    suggested_queue: str


class InboundEmail(BaseModel):
    external_id: str
    channel: str = "email"
    from_email: str
    subject: str
    body: str


class RefundAction(BaseModel):
    ticket_id: str
    amount: float
    reason: str