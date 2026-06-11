from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from catalogo_service.api.schemas import ProdutoResponse
from catalogo_service.application.queries import ProdutoQueries

router = APIRouter(tags=["produtos"])


def get_queries(request: Request) -> ProdutoQueries:
    return request.app.state.queries


@router.get("/produtos", response_model=list[ProdutoResponse])
async def listar_produtos(queries: ProdutoQueries = Depends(get_queries)):
    produtos = await queries.listar()
    return [ProdutoResponse(id=item.id, nome=item.nome, preco=item.preco, estoque=item.estoque) for item in produtos]


@router.get("/produtos/{produto_id}", response_model=ProdutoResponse)
async def obter_produto(produto_id: UUID, queries: ProdutoQueries = Depends(get_queries)):
    produto = await queries.obter(produto_id)
    if produto is None:
        return JSONResponse(
            status_code=404,
            media_type="application/problem+json",
            content={
                "type": "about:blank",
                "title": "Produto nao encontrado",
                "status": 404,
                "detail": f"Produto {produto_id} nao existe.",
            },
        )
    return ProdutoResponse(id=produto.id, nome=produto.nome, preco=produto.preco, estoque=produto.estoque)

