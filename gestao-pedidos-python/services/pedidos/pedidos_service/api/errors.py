from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from pedidos_service.application.commands import ProdutoIndisponivel
from pedidos_service.domain.entities import DomainError


class ProblemError(Exception):
    def __init__(self, status: int, title: str, detail: str, type_: str = "about:blank") -> None:
        self.status = status
        self.title = title
        self.detail = detail
        self.type = type_


def problem_response(status: int, title: str, detail: str, type_: str = "about:blank") -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "type": type_,
            "title": title,
            "status": status,
            "detail": detail,
        },
        media_type="application/problem+json",
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ProblemError)
    async def handle_problem_error(request: Request, exc: ProblemError) -> JSONResponse:
        return problem_response(exc.status, exc.title, exc.detail, exc.type)

    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        return problem_response(422, "Regra de negocio violada", str(exc))

    @app.exception_handler(ProdutoIndisponivel)
    async def handle_produto_error(request: Request, exc: ProdutoIndisponivel) -> JSONResponse:
        return problem_response(409, "Produto indisponivel", str(exc))

