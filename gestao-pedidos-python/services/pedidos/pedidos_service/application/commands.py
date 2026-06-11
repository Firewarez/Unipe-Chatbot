from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from pedidos_service.domain.entities import ItemPedido, Money, Pedido
from pedidos_service.domain.events import DomainEvent


class ProdutoIndisponivel(Exception):
    pass


@dataclass(frozen=True)
class CriarPedidoItem:
    produto_id: UUID
    quantidade: int


@dataclass(frozen=True)
class CriarPedidoCommand:
    cliente_id: UUID
    itens: list[CriarPedidoItem]


@dataclass(frozen=True)
class ProdutoCatalogo:
    id: UUID
    nome: str
    preco: Decimal
    estoque: int


class PedidoRepository(Protocol):
    async def adicionar(self, pedido: Pedido) -> None:
        ...

    async def obter(self, pedido_id: UUID) -> Pedido | None:
        ...

    async def atualizar(self, pedido: Pedido) -> None:
        ...

    async def remover(self, pedido_id: UUID) -> None:
        ...


class CatalogoClient(Protocol):
    async def obter_produto(self, produto_id: UUID) -> ProdutoCatalogo | None:
        ...


class EventPublisher(Protocol):
    async def publicar(self, event: DomainEvent) -> None:
        ...


class CriarPedidoHandler:
    def __init__(
        self,
        repository: PedidoRepository,
        catalogo_client: CatalogoClient,
        publisher: EventPublisher,
    ) -> None:
        self.repository = repository
        self.catalogo_client = catalogo_client
        self.publisher = publisher

    async def handle(self, command: CriarPedidoCommand) -> Pedido:
        itens: list[ItemPedido] = []

        for item in command.itens:
            produto = await self.catalogo_client.obter_produto(item.produto_id)
            if produto is None:
                raise ProdutoIndisponivel(f"Produto {item.produto_id} nao encontrado.")
            if produto.estoque < item.quantidade:
                raise ProdutoIndisponivel(f"Produto {produto.nome} sem estoque suficiente.")
            itens.append(
                ItemPedido(
                    produto_id=produto.id,
                    quantidade=item.quantidade,
                    preco_unitario=Money(produto.preco),
                )
            )

        pedido = Pedido.criar(cliente_id=command.cliente_id, itens=itens)
        await self.repository.adicionar(pedido)

        for event in pedido.pull_events():
            await self.publisher.publicar(event)

        return pedido

