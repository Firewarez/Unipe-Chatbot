"""Messaging infrastructure."""
import logging
from chat.api.config import settings
from .noop_event_bus import NoopEventBus
from .rabbitmq_event_bus import RabbitMQEventBus

logger = logging.getLogger(__name__)


def get_event_bus():
	if not settings.MESSAGING_ENABLED:
		return NoopEventBus()
	try:
		return RabbitMQEventBus(url=settings.RABBITMQ_URL, exchange=settings.RABBITMQ_EXCHANGE)
	except Exception as exc:
		logger.warning("Messaging disabled due to error: %s", exc)
		return NoopEventBus()
