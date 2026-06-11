from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from pedidos_service.domain.events import DomainEvent, PedidoCriadoEvent


class DomainError(Exception):
    """Erro de regra de negocio."""


class StatusPedido(StrEnum):
    CRIADO = "criado"
    PAGO = "pago"
    CANCELADO = "cancelado"


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "BRL"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise DomainError("Valor monetario nao pode ser negativo.")
        if len(self.currency) != 3:
            raise DomainError("Moeda deve seguir ISO 4217, como BRL.")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise DomainError("Nao e possivel somar moedas diferentes.")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, quantity: int) -> "Money":
        if quantity <= 0:
            raise DomainError("Quantidade deve ser positiva.")
        return Money(self.amount * quantity, self.currency)


@dataclass(frozen=True)
class ItemPedido:
    produto_id: UUID
    quantidade: int
    preco_unitario: Money

    def __post_init__(self) -> None:
        if self.quantidade <= 0:
            raise DomainError("Quantidade do item deve ser maior que zero.")

    @property
    def subtotal(self) -> Money:
        return self.preco_unitario * self.quantidade


@dataclass
class Pedido:
    id: UUID
    cliente_id: UUID
    itens: list[ItemPedido]
    status: StatusPedido = StatusPedido.CRIADO
    criado_em: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    eventos: list[DomainEvent] = field(default_factory=list)

    @classmethod
    def criar(cls, cliente_id: UUID, itens: list[ItemPedido]) -> "Pedido":
        if not itens:
            raise DomainError("Pedido deve possuir ao menos um item.")
        pedido = cls(id=uuid4(), cliente_id=cliente_id, itens=itens)
        pedido.eventos.append(
            PedidoCriadoEvent(
                event_id=uuid4(),
                occurred_at=pedido.criado_em,
                pedido_id=pedido.id,
                cliente_id=pedido.cliente_id,
                total=pedido.total.amount,
            )
        )
        return pedido

    @property
    def total(self) -> Money:
        total = Money(Decimal("0.00"))
        for item in self.itens:
            total = total + item.subtotal
        return total

    def marcar_pago(self) -> None:
        if self.status == StatusPedido.CANCELADO:
            raise DomainError("Pedido cancelado nao pode ser pago.")
        self.status = StatusPedido.PAGO

    def cancelar(self) -> None:
        if self.status == StatusPedido.PAGO:
            raise DomainError("Pedido pago nao pode ser cancelado.")
        self.status = StatusPedido.CANCELADO

    def pull_events(self) -> list[DomainEvent]:
        events = list(self.eventos)
        self.eventos.clear()
        return events

