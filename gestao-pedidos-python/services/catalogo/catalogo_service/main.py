from fastapi import FastAPI

from catalogo_service.api.routes import router
from catalogo_service.application.queries import ProdutoQueries
from catalogo_service.infrastructure.repositories import InMemoryProdutoRepository


def create_app() -> FastAPI:
    app = FastAPI(
        title="GestaoPedidos.Catalogo",
        version="0.1.0",
        description="API RESTful de catalogo em Python.",
    )
    app.state.queries = ProdutoQueries(InMemoryProdutoRepository())
    app.include_router(router, prefix="/api")
    return app


app = create_app()

