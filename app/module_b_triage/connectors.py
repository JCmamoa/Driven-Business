import httpx
from app.schemas import InboundEmail


class GmailConnector:
    def __init__(self, token: str):
        self.token = token

    async def fetch_unread(self) -> list[InboundEmail]:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                headers={"Authorization": f"Bearer {self.token}"},
                params={"q": "is:unread"},
            )
            r.raise_for_status()
            return []


class WebhookConnector:
    @staticmethod
    def parse_zendesk(payload: dict) -> InboundEmail:
        ticket = payload["ticket"]
        return InboundEmail(
            external_id=str(ticket["id"]),
            channel="zendesk",
            from_email=ticket.get("requester", {}).get("email", ""),
            subject=ticket.get("subject", ""),
            body=ticket.get("description", ""),
        )