import json
import asyncio
import aio_pika

from app.config import settings
from app.observability.logging import get_logger

log = get_logger("dlq")


async def consume_with_dlq(queue_name: str, handler, max_retries: int = 3):
    conn = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await conn.channel()
    await channel.set_qos(prefetch_count=10)
    exchange = await channel.declare_exchange(
        "aiops.events", aio_pika.ExchangeType.TOPIC, durable=True
    )

    dlq = await channel.declare_queue(f"{queue_name}.dlq", durable=True)
    await dlq.bind(exchange, routing_key=f"dlq.{queue_name}")

    queue = await channel.declare_queue(queue_name, durable=True)

    async with queue.iterator() as it:
        async for message in it:
            async with message.process(requeue=False):
                key = message.headers.get("x-idempotency-key", message.message_id)
                retries = int(message.headers.get("x-retries", 0))
                try:
                    await handler(json.loads(message.body), key)
                except Exception as exc:
                    log.warning("handler_failed", key=key, retries=retries, error=str(exc))
                    if retries + 1 >= max_retries:
                        await exchange.publish(
                            aio_pika.Message(
                                body=message.body,
                                headers={**message.headers, "x-retries": retries + 1},
                            ),
                            routing_key=f"dlq.{queue_name}",
                        )
                    else:
                        delay = 2 ** retries
                        await asyncio.sleep(delay)
                        await exchange.publish(
                            aio_pika.Message(
                                body=message.body,
                                headers={**message.headers, "x-retries": retries + 1},
                            ),
                            routing_key=message.routing_key,
                        )