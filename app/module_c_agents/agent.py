import json
import uuid
from google import genai
from google.genai import types

from app.config import settings
from app.db import SessionLocal
from app.models import Ticket, AgentTrace
from app.module_c_agents import tools, rag, guardrails
from app.observability.logging import get_logger

log = get_logger("agent")
_client = genai.Client(api_key=settings.gemini_api_key)

TOOL_MAP = {
    "lookup_order": tools.lookup_order,
    "generate_return_label": tools.generate_return_label,
    "issue_exchange_coupon": tools.issue_exchange_coupon,
    "issue_refund": tools.issue_refund,
    "check_product_stock": tools.check_product_stock,
}

TOOL_DECLS = [
    {
        "name": "lookup_order",
        "description": "Consulta o status de um pedido pelo ID.",
        "parameters": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "generate_return_label",
        "description": "Gera etiqueta de logística reversa.",
        "parameters": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "issue_exchange_coupon",
        "description": "Emite cupom de troca.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "amount": {"type": "number"},
            },
            "required": ["order_id", "amount"],
        },
    },
    {
        "name": "issue_refund",
        "description": "Emite reembolso. Requer aprovação humana acima do limite.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "amount": {"type": "number"},
            },
            "required": ["order_id", "amount"],
        },
    },
    {
        "name": "check_product_stock",
        "description": "Verifica estoque e preço de um SKU.",
        "parameters": {
            "type": "object",
            "properties": {"sku": {"type": "string"}},
            "required": ["sku"],
        },
    },
]


def _trace(ticket_id: str, step: str, payload: dict) -> None:
    with SessionLocal() as session:
        session.add(
            AgentTrace(ticket_id=uuid.UUID(ticket_id), step=step, payload=payload)
        )
        session.commit()


async def run_agent(ticket_id: str, user_message: str) -> dict:
    with SessionLocal() as session:
        ticket = session.get(Ticket, uuid.UUID(ticket_id))
        if not ticket:
            raise ValueError("Ticket não encontrado")
        intent = ticket.intent or "other"
        summary = ticket.summary or ""

    context_docs = rag.retrieve(user_message)
    context_block = "\n".join(context_docs)

    sys_prompt = f"""Você é um agente de suporte de e-commerce.
Intenção detectada: {intent}. Resumo: {summary}.
Políticas relevantes:\n{context_block}
Use ferramentas quando necessário. Para reembolsos acima de
R${settings.refund_human_approval_threshold}, solicite aprovação humana
(mencione que será enviado para aprovação) e NÃO chame issue_refund."""

    contents = [sys_prompt, user_message]
    config = types.GenerateContentConfig(
        tools=[{"function_declarations": TOOL_DECLS}],
        temperature=0.2,
    )

    for step in range(6):
        resp = _client.models.generate_content(
            model=settings.gemini_model, contents=contents, config=config
        )
        _trace(ticket_id, f"llm_step_{step}", {"text": resp.text})

        if not resp.function_calls:
            return {"final": resp.text, "steps": step + 1}

        for call in resp.function_calls:
            name, args = call.name, dict(call.args or {})
            _trace(ticket_id, "tool_call", {"name": name, "args": args})

            if name == "issue_refund" and guardrails.requires_human_approval(
                "refund", float(args.get("amount", 0))
            ):
                approval_id = guardrails.create_approval_request(
                    ticket_id, "refund", float(args["amount"])
                )
                result = {
                    "status": "pending_human_approval",
                    "approval_id": approval_id,
                }
            else:
                fn = TOOL_MAP[name]
                result = await fn(**args)

            contents.append(
                types.Content(
                    role="tool",
                    parts=[
                        types.Part.from_function_response(
                            name=name, response={"result": json.dumps(result, default=str)}
                        )
                    ],
                )
            )

    return {"final": "limite de passos atingido", "steps": 6}