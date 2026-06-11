import json
from decimal import Decimal
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Engine

from pedidos_service.application.queries import ListarPedidosQuery, PedidoReadModel
from pedidos_service.infrastructure.cache import Cache


class SqlAlchemyPedidoQueries:
    def __init__(self, engine: Engine, cache: Cache) -> None:
        self.engine = engine
        self.cache = cache

    async def listar(self, query: ListarPedidosQuery) -> list[PedidoReadModel]:
        cache_key = f"pedidos:pagina:{query.pagina}:tamanho:{query.tamanho}"
        cached = await self.cache.get(cache_key)
        if cached:
            return [
                PedidoReadModel(
                    id=UUID(item["id"]),
                    cliente_id=UUID(item["cliente_id"]),
                    status=item["status"],
                    total=Decimal(item["total"]),
                )
                for item in json.loads(cached)
            ]

        offset = (query.pagina - 1) * query.tamanho
        sql = text(
            """
            SELECT id, cliente_id, status, total
            FROM pedidos
            ORDER BY criado_em DESC
            OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
            """
        )

        if self.engine.dialect.name == "sqlite":
            sql = text(
                """
                SELECT id, cliente_id, status, total
                FROM pedidos
                ORDER BY criado_em DESC
                LIMIT :limit OFFSET :offset
                """
            )

        with self.engine.begin() as connection:
            rows = connection.execute(sql, {"offset": offset, "limit": query.tamanho}).mappings().all()

        result = [
            PedidoReadModel(
                id=UUID(row["id"]),
                cliente_id=UUID(row["cliente_id"]),
                status=row["status"],
                total=Decimal(row["total"]),
            )
            for row in rows
        ]

        await self.cache.set(
            cache_key,
            json.dumps(
                [
                    {
                        "id": str(item.id),
                        "cliente_id": str(item.cliente_id),
                        "status": item.status,
                        "total": str(item.total),
                    }
                    for item in result
                ]
            ),
        )
        return result

