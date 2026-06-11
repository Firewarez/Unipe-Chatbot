from decimal import Decimal
from uuid import UUID

import pytest

from pedidos_service.application.commands import (
    CriarPedidoCommand,
    CriarPedidoHandler,
    CriarPedidoItem,
    ProdutoCatalogo,
    ProdutoIndisponivel,
)


PRODUTO_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
CLIENTE_ID = UUID("11111111-1111-1111-1111-111111111111")


class FakeRepository:
    def __init__(self):
        self.pedidos = []

    async def adicionar(self, pedido):
        self.pedidos.append(pedido)

    async def obter(self, pedido_id):
        return next((pedido for pedido in self.pedidos if pedido.id == pedido_id), None)

    async def atualizar(self, pedido):
        return None

    async def remover(self, pedido_id):
        self.pedidos = [pedido for pedido in self.pedidos if pedido.id != pedido_id]


class FakeCatalogoClient:
    async def obter_produto(self, produto_id):
        return ProdutoCatalogo(id=produto_id, nome="Notebook Pro", preco=Decimal("4800.00"), estoque=10)


class FakeCatalogoSemEstoque:
    async def obter_produto(self, produto_id):
        return ProdutoCatalogo(id=produto_id, nome="Notebook Pro", preco=Decimal("4800.00"), estoque=0)


class FakePublisher:
    def __init__(self):
        self.events = []

    async def publicar(self, event):
        self.events.append(event)


@pytest.mark.asyncio
async def test_cria_pedido_e_publica_domain_event():
    repository = FakeRepository()
    publisher = FakePublisher()
    handler = CriarPedidoHandler(repository, FakeCatalogoClient(), publisher)

    pedido = await handler.handle(
        CriarPedidoCommand(
            cliente_id=CLIENTE_ID,
            itens=[CriarPedidoItem(produto_id=PRODUTO_ID, quantidade=2)],
        )
    )

    assert pedido.id is not None
    assert pedido.total.amount == Decimal("9600.00")
    assert repository.pedidos == [pedido]
    assert len(publisher.events) == 1
    assert publisher.events[0].pedido_id == pedido.id


@pytest.mark.asyncio
async def test_recusa_pedido_quando_produto_nao_tem_estoque():
    handler = CriarPedidoHandler(FakeRepository(), FakeCatalogoSemEstoque(), FakePublisher())

    with pytest.raises(ProdutoIndisponivel):
        await handler.handle(
            CriarPedidoCommand(
                cliente_id=CLIENTE_ID,
                itens=[CriarPedidoItem(produto_id=PRODUTO_ID, quantidade=2)],
            )
        )

