from sqlalchemy import Column, DateTime, ForeignKey, Integer, MetaData, Numeric, String, Table, create_engine
from sqlalchemy.engine import Engine


metadata = MetaData()

pedidos_table = Table(
    "pedidos",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("cliente_id", String(36), nullable=False, index=True),
    Column("status", String(20), nullable=False),
    Column("total", Numeric(12, 2), nullable=False),
    Column("criado_em", DateTime(timezone=True), nullable=False),
)

itens_pedido_table = Table(
    "itens_pedido",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("pedido_id", String(36), ForeignKey("pedidos.id"), nullable=False, index=True),
    Column("produto_id", String(36), nullable=False),
    Column("quantidade", Integer, nullable=False),
    Column("preco_unitario", Numeric(12, 2), nullable=False),
)


def create_database_engine(database_url: str) -> Engine:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, future=True, pool_pre_ping=True, connect_args=connect_args)


def init_database(engine: Engine) -> None:
    metadata.create_all(engine)

