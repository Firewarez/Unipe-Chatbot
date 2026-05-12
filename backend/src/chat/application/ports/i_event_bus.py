"""Port: IEventBus."""
from abc import ABC, abstractmethod
from chat.domain.events.integration_event import IntegrationEvent


class IEventBus(ABC):
    @abstractmethod
    def publish(self, event: IntegrationEvent) -> None:
        pass
