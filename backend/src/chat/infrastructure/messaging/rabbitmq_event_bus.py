"""RabbitMQ event bus implementation."""
import json
import logging
from datetime import datetime, timezone

from chat.application.ports.i_event_bus import IEventBus
from chat.domain.events.integration_event import IntegrationEvent

logger = logging.getLogger(__name__)


class RabbitMQEventBus(IEventBus):
    def __init__(self, url: str, exchange: str):
        self._url = url
        self._exchange = exchange
        try:
            import pika  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("pika is required to publish to RabbitMQ") from exc
        self._pika = pika

    def publish(self, event: IntegrationEvent) -> None:
        self.publish_payload(event.to_dict(), event.event_type, event.event_id)

    def publish_payload(self, payload: dict, event_type: str, event_id: str | None = None) -> None:
        payload_json = json.dumps(payload, ensure_ascii=False)
        params = self._pika.URLParameters(self._url)
        connection = self._pika.BlockingConnection(params)
        try:
            channel = connection.channel()
            channel.exchange_declare(exchange=self._exchange, exchange_type="topic", durable=True)
            properties = self._pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
                message_id=event_id,
                timestamp=int(datetime.now(timezone.utc).timestamp()),
            )
            channel.basic_publish(
                exchange=self._exchange,
                routing_key=event_type,
                body=payload_json.encode("utf-8"),
                properties=properties,
            )
        finally:
            connection.close()
