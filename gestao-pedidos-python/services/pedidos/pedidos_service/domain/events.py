from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class DomainEvent:
    event_id: UUID
    occurred_at: datetime


@dataclass(frozen=True)
class PedidoCriadoEvent(DomainEvent):
    pedido_id: UUID
    cliente_id: UUID
    total: Decimal

