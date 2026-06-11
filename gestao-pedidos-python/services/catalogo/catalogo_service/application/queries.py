from typing import Protocol
from uuid import UUID

from catalogo_service.domain.entities import Produto


class ProdutoRepository(Protocol):
    async def listar(self) -> list[Produto]:
        ...

    async def obter(self, produto_id: UUID) -> Produto | None:
        ...


class ProdutoQueries:
    def __init__(self, repository: ProdutoRepository) -> None:
        self.repository = repository

    async def listar(self) -> list[Produto]:
        return await self.repository.listar()

    async def obter(self, produto_id: UUID) -> Produto | None:
        return await self.repository.obter(produto_id)

