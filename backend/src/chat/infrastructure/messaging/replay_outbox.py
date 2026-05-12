"""Manual outbox replay helper."""
import json
from chat.api.config import settings
from chat.infrastructure.data.database import SessionLocal
from chat.infrastructure.data.outbox_repository import OutboxRepository
from chat.infrastructure.messaging.rabbitmq_event_bus import RabbitMQEventBus


def replay_pending(limit: int = 100) -> int:
    db = SessionLocal()
    try:
        repo = OutboxRepository(db)
        bus = RabbitMQEventBus(url=settings.RABBITMQ_URL, exchange=settings.RABBITMQ_EXCHANGE)
        pending = repo.list_pending(limit=limit)
        for item in pending:
            payload = json.loads(item.payload)
            bus.publish_payload(payload, item.event_type, item.id)
            repo.mark_published(item.id)
        return len(pending)
    finally:
        db.close()


if __name__ == "__main__":
    count = replay_pending()
    print(f"Replayed {count} outbox events")
