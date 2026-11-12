import asyncio
from app.messaging.outbox import publish_pending
from app.observability.logging import get_logger

log = get_logger("outbox_publisher")


async def main() -> None:
    log.info("outbox_publisher_started")
    while True:
        try:
            n = await publish_pending()
            if n:
                log.info("outbox_published", count=n)
        except Exception as exc:
            log.error("outbox_error", error=str(exc))
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())