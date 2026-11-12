import asyncio
from app.messaging.dlq import consume_with_dlq
from app.module_c_agents.agent import run_agent
from app.observability.logging import get_logger

log = get_logger("agent_worker")


async def handle(payload: dict, idempotency_key: str) -> None:
    result = await run_agent(payload["ticket_id"], payload["message"])
    log.info("agent_finished", ticket_id=payload["ticket_id"], result=result)


async def main() -> None:
    log.info("agent_worker_started")
    await consume_with_dlq("agent.queue", handle)


if __name__ == "__main__":
    asyncio.run(main())