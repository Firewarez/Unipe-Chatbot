from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class ListarPedidosQuery:
    pagina: int = 1
    tamanho: int = 20


@dataclass(frozen=True)
class PedidoReadModel:
    id: UUID
    cliente_id: UUID
    status: str
    total: Decimal


class PedidoQueries(Protocol):
    async def listar(self, query: ListarPedidosQuery) -> list[PedidoReadModel]:
        ...

