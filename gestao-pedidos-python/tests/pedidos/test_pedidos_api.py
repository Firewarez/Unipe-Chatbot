from decimal import Decimal
from uuid import UUID

from fastapi.testclient import TestClient

from pedidos_service.application.commands import ProdutoCatalogo
from pedidos_service.config import Settings
from pedidos_service.main import create_app


PRODUTO_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
CLIENTE_ID = UUID("11111111-1111-1111-1111-111111111111")


class CatalogoFake:
    async def obter_produto(self, produto_id):
        return ProdutoCatalogo(id=produto_id, nome="Notebook Pro", preco=Decimal("4800.00"), estoque=10)


class PublisherFake:
    def __init__(self):
        self.events = []

    async def publicar(self, event):
        self.events.append(event)


def test_post_pedidos_retorna_201_e_location(tmp_path):
    app = create_app(
        Settings(database_url=f"sqlite:///{tmp_path}/pedidos.db"),
        use_external_infra=False,
    )
    publisher = PublisherFake()
    app.state.catalogo_client = CatalogoFake()
    app.state.publisher = publisher

    client = TestClient(app)
    response = client.post(
        "/api/pedidos",
        json={
            "cliente_id": str(CLIENTE_ID),
            "itens": [{"produto_id": str(PRODUTO_ID), "quantidade": 2}],
        },
    )

    assert response.status_code == 201
    assert response.headers["location"].startswith("/api/pedidos/")
    assert response.json()["total"] == "9600.00"
    assert len(publisher.events) == 1


def test_get_pedido_inexistente_retorna_problem_details(tmp_path):
    app = create_app(
        Settings(database_url=f"sqlite:///{tmp_path}/pedidos.db"),
        use_external_infra=False,
    )
    client = TestClient(app)

    response = client.get("/api/pedidos/22222222-2222-2222-2222-222222222222")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["title"] == "Pedido nao encontrado"

