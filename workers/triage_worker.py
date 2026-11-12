import asyncio
from app.messaging.dlq import consume_with_dlq
from app.module_b_triage.pipeline import process_inbound
from app.observability.logging import get_logger

log = get_logger("triage_worker")


async def handle(payload: dict, idempotency_key: str) -> None:
    await process_inbound(payload, idempotency_key)


async def main() -> None:
    log.info("triage_worker_started")
    await consume_with_dlq("triage.queue", handle)


if __name__ == "__main__":
    asyncio.run(main())