from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Engine

from pedidos_service.domain.entities import ItemPedido, Money, Pedido, StatusPedido
from pedidos_service.infrastructure.database import itens_pedido_table, pedidos_table


class SqlAlchemyPedidoRepository:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    async def adicionar(self, pedido: Pedido) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                insert(pedidos_table).values(
                    id=str(pedido.id),
                    cliente_id=str(pedido.cliente_id),
                    status=pedido.status.value,
                    total=pedido.total.amount,
                    criado_em=pedido.criado_em,
                )
            )
            connection.execute(
                insert(itens_pedido_table),
                [
                    {
                        "pedido_id": str(pedido.id),
                        "produto_id": str(item.produto_id),
                        "quantidade": item.quantidade,
                        "preco_unitario": item.preco_unitario.amount,
                    }
                    for item in pedido.itens
                ],
            )

    async def obter(self, pedido_id: UUID) -> Pedido | None:
        with self.engine.begin() as connection:
            pedido_row = connection.execute(
                select(pedidos_table).where(pedidos_table.c.id == str(pedido_id))
            ).mappings().first()
            if pedido_row is None:
                return None

            item_rows = connection.execute(
                select(itens_pedido_table).where(itens_pedido_table.c.pedido_id == str(pedido_id))
            ).mappings().all()

        itens = [
            ItemPedido(
                produto_id=UUID(row["produto_id"]),
                quantidade=row["quantidade"],
                preco_unitario=Money(Decimal(row["preco_unitario"])),
            )
            for row in item_rows
        ]

        return Pedido(
            id=UUID(pedido_row["id"]),
            cliente_id=UUID(pedido_row["cliente_id"]),
            status=StatusPedido(pedido_row["status"]),
            criado_em=pedido_row["criado_em"],
            itens=itens,
        )

    async def atualizar(self, pedido: Pedido) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                update(pedidos_table)
                .where(pedidos_table.c.id == str(pedido.id))
                .values(status=pedido.status.value, total=pedido.total.amount)
            )

    async def remover(self, pedido_id: UUID) -> None:
        with self.engine.begin() as connection:
            connection.execute(delete(itens_pedido_table).where(itens_pedido_table.c.pedido_id == str(pedido_id)))
            connection.execute(delete(pedidos_table).where(pedidos_table.c.id == str(pedido_id)))

