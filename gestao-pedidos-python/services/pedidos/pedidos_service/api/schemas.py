from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CriarPedidoItemRequest(BaseModel):
    produto_id: UUID
    quantidade: int = Field(gt=0)


class CriarPedidoRequest(BaseModel):
    cliente_id: UUID
    itens: list[CriarPedidoItemRequest]


class AtualizarStatusRequest(BaseModel):
    status: str = Field(pattern="^(pago|cancelado)$")


class ItemPedidoResponse(BaseModel):
    produto_id: UUID
    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal


class PedidoResponse(BaseModel):
    id: UUID
    cliente_id: UUID
    status: str
    total: Decimal
    itens: list[ItemPedidoResponse]


class PedidoListaResponse(BaseModel):
    id: UUID
    cliente_id: UUID
    status: str
    total: Decimal

