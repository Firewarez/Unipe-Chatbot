"""Publisher that writes to outbox and attempts immediate dispatch."""
import logging
from chat.application.ports.i_event_bus import IEventBus
from chat.application.ports.i_event_publisher import IEventPublisher
from chat.domain.events.integration_event import IntegrationEvent
from chat.infrastructure.data.outbox_repository import OutboxRepository

logger = logging.getLogger(__name__)


class OutboxEventPublisher(IEventPublisher):
    def __init__(self, outbox_repo: OutboxRepository, event_bus: IEventBus):
        self._outbox_repo = outbox_repo
        self._event_bus = event_bus

    def publish(self, event: IntegrationEvent) -> None:
        self._outbox_repo.add(event)
        try:
            self._event_bus.publish(event)
            self._outbox_repo.mark_published(event.event_id)
        except Exception as exc:
            logger.warning("Failed to publish event %s: %s", event.event_type, exc)
