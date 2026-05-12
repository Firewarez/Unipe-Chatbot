"""Port: IEventPublisher."""
from abc import ABC, abstractmethod
from chat.domain.events.integration_event import IntegrationEvent


class IEventPublisher(ABC):
    @abstractmethod
    def publish(self, event: IntegrationEvent) -> None:
        pass
