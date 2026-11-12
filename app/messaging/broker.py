import json
import aio_pika
from aio_pika import ExchangeType, Message, DeliveryMode

from app.config import settings

_connection: aio_pika.RobustConnection | None = None
_channel: aio_pika.abc.AbstractRobustChannel | None = None
_exchange: aio_pika.abc.AbstractRobustExchange | None = None


async def get_exchange() -> aio_pika.abc.AbstractRobustExchange:
    global _connection, _channel, _exchange
    if _exchange is None:
        _connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        _channel = await _connection.channel()
        _exchange = await _channel.declare_exchange(
            "aiops.events", ExchangeType.TOPIC, durable=True
        )
    return _exchange


async def publish(topic: str, payload: dict, idempotency_key: str) -> None:
    exchange = await get_exchange()
    msg = Message(
        body=json.dumps(payload).encode(),
        delivery_mode=DeliveryMode.PERSISTENT,
        message_id=idempotency_key,
        headers={"x-idempotency-key": idempotency_key},
    )
    await exchange.publish(msg, routing_key=topic)