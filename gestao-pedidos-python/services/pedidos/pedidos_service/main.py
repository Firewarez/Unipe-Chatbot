from fastapi import FastAPI

from pedidos_service.api.errors import register_exception_handlers
from pedidos_service.api.routes import router
from pedidos_service.config import Settings
from pedidos_service.infrastructure.cache import NullCache, RedisCache
from pedidos_service.infrastructure.catalog_client import CatalogoHttpClient
from pedidos_service.infrastructure.database import create_database_engine, init_database
from pedidos_service.infrastructure.message_bus import LoggingEventPublisher, RabbitMqEventPublisher
from pedidos_service.infrastructure.queries import SqlAlchemyPedidoQueries
from pedidos_service.infrastructure.repositories import SqlAlchemyPedidoRepository


def create_app(settings: Settings | None = None, use_external_infra: bool = True) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(
        title="GestaoPedidos.Pedidos",
        version="0.1.0",
        description="API RESTful de pedidos em Python com Clean Architecture, CQRS, cache e mensageria.",
    )
    register_exception_handlers(app)
    app.include_router(router, prefix="/api")

    engine = create_database_engine(settings.database_url)
    init_database(engine)

    cache = RedisCache(settings.redis_url, settings.cache_ttl_seconds) if use_external_infra else NullCache()
    app.state.repository = SqlAlchemyPedidoRepository(engine)
    app.state.queries = SqlAlchemyPedidoQueries(engine, cache)
    app.state.catalogo_client = CatalogoHttpClient(settings.catalogo_base_url)
    app.state.publisher = RabbitMqEventPublisher(settings.rabbitmq_url) if use_external_infra else LoggingEventPublisher()
    return app


app = create_app()

