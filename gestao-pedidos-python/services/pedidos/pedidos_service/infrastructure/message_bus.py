import json
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from aio_pika import ExchangeType, Message, connect_robust

from pedidos_service.domain.events import DomainEvent


class LoggingEventPublisher:
    async def publicar(self, event: DomainEvent) -> None:
        print(f"Domain event publicado localmente: {event}")


class RabbitMqEventPublisher:
    def __init__(self, rabbitmq_url: str) -> None:
        self.rabbitmq_url = rabbitmq_url

    async def publicar(self, event: DomainEvent) -> None:
        connection = await connect_robust(self.rabbitmq_url)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange("pedidos.events", ExchangeType.TOPIC, durable=True)
            await exchange.publish(
                Message(
                    body=json.dumps(_to_jsonable(asdict(event))).encode("utf-8"),
                    content_type="application/json",
                    message_id=str(event.event_id),
                ),
                routing_key="pedido.criado",
            )


def _to_jsonable(value):
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value
