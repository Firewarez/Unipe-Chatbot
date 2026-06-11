from decimal import Decimal
from uuid import UUID

from catalogo_service.domain.entities import Produto


class InMemoryProdutoRepository:
    def __init__(self) -> None:
        self._produtos = {
            UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"): Produto(
                id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
                nome="Notebook Pro",
                preco=Decimal("4800.00"),
                estoque=8,
            ),
            UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"): Produto(
                id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                nome="Mouse Sem Fio",
                preco=Decimal("149.90"),
                estoque=40,
            ),
            UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"): Produto(
                id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
                nome="Monitor 27",
                preco=Decimal("1299.00"),
                estoque=12,
            ),
        }

    async def listar(self) -> list[Produto]:
        return list(self._produtos.values())

    async def obter(self, produto_id: UUID) -> Produto | None:
        return self._produtos.get(produto_id)

