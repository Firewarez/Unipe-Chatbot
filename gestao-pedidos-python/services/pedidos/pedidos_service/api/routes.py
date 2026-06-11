from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status

from pedidos_service.api.errors import ProblemError
from pedidos_service.api.schemas import (
    AtualizarStatusRequest,
    CriarPedidoRequest,
    ItemPedidoResponse,
    PedidoListaResponse,
    PedidoResponse,
)
from pedidos_service.application.commands import CriarPedidoCommand, CriarPedidoHandler, CriarPedidoItem
from pedidos_service.application.queries import ListarPedidosQuery
from pedidos_service.domain.entities import Pedido

router = APIRouter(tags=["pedidos"])


def get_repository(request: Request):
    return request.app.state.repository


def get_queries(request: Request):
    return request.app.state.queries


def get_catalogo_client(request: Request):
    return request.app.state.catalogo_client


def get_publisher(request: Request):
    return request.app.state.publisher


@router.post("/pedidos", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
async def criar_pedido(
    payload: CriarPedidoRequest,
    response: Response,
    repository=Depends(get_repository),
    catalogo_client=Depends(get_catalogo_client),
    publisher=Depends(get_publisher),
):
    handler = CriarPedidoHandler(repository, catalogo_client, publisher)
    pedido = await handler.handle(
        CriarPedidoCommand(
            cliente_id=payload.cliente_id,
            itens=[CriarPedidoItem(produto_id=item.produto_id, quantidade=item.quantidade) for item in payload.itens],
        )
    )
    response.headers["Location"] = f"/api/pedidos/{pedido.id}"
    return _to_response(pedido)


@router.get("/pedidos", response_model=list[PedidoListaResponse])
async def listar_pedidos(
    pagina: int = 1,
    tamanho: int = 20,
    queries=Depends(get_queries),
):
    result = await queries.listar(ListarPedidosQuery(pagina=pagina, tamanho=tamanho))
    return [PedidoListaResponse(id=item.id, cliente_id=item.cliente_id, status=item.status, total=item.total) for item in result]


@router.get("/pedidos/{pedido_id}", response_model=PedidoResponse)
async def obter_pedido(pedido_id: UUID, repository=Depends(get_repository)):
    pedido = await repository.obter(pedido_id)
    if pedido is None:
        raise ProblemError(404, "Pedido nao encontrado", f"Pedido {pedido_id} nao existe.")
    return _to_response(pedido)


@router.put("/pedidos/{pedido_id}/status", response_model=PedidoResponse)
async def atualizar_status(
    pedido_id: UUID,
    payload: AtualizarStatusRequest,
    repository=Depends(get_repository),
):
    pedido = await repository.obter(pedido_id)
    if pedido is None:
        raise ProblemError(404, "Pedido nao encontrado", f"Pedido {pedido_id} nao existe.")

    if payload.status == "pago":
        pedido.marcar_pago()
    elif payload.status == "cancelado":
        pedido.cancelar()

    await repository.atualizar(pedido)
    return _to_response(pedido)


@router.delete("/pedidos/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_pedido(pedido_id: UUID, repository=Depends(get_repository)):
    pedido = await repository.obter(pedido_id)
    if pedido is None:
        raise ProblemError(404, "Pedido nao encontrado", f"Pedido {pedido_id} nao existe.")
    await repository.remover(pedido_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _to_response(pedido: Pedido) -> PedidoResponse:
    return PedidoResponse(
        id=pedido.id,
        cliente_id=pedido.cliente_id,
        status=pedido.status.value,
        total=pedido.total.amount,
        itens=[
            ItemPedidoResponse(
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                preco_unitario=item.preco_unitario.amount,
                subtotal=item.subtotal.amount,
            )
            for item in pedido.itens
        ],
    )

