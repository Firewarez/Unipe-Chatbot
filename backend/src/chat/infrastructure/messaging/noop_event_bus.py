"""No-op event bus used when messaging is disabled or unavailable."""
import logging
from chat.application.ports.i_event_bus import IEventBus
from chat.domain.events.integration_event import IntegrationEvent

logger = logging.getLogger(__name__)


class NoopEventBus(IEventBus):
    def publish(self, event: IntegrationEvent) -> None:
        logger.info("Event bus disabled; skipping publish of %s", event.event_type)
