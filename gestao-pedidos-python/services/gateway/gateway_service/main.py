import os
import json
from pathlib import Path

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse


def load_gateway_config() -> tuple[list[dict], dict[str, dict]]:
    config_path = Path(__file__).with_name("routes.json")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    clusters = config["clusters"]
    env_overrides = {
        "pedidos-cluster": os.getenv("PEDIDOS_BASE_URL"),
        "catalogo-cluster": os.getenv("CATALOGO_BASE_URL"),
        "notificacoes-cluster": os.getenv("NOTIFICACOES_BASE_URL"),
    }
    for cluster_id, destination in env_overrides.items():
        if destination:
            clusters[cluster_id]["destination"] = destination
    return config["routes"], clusters


ROUTES, CLUSTERS = load_gateway_config()


def create_app() -> FastAPI:
    app = FastAPI(
        title="GestaoPedidos.Gateway",
        version="0.1.0",
        description="API Gateway Python com rotas e clusters no estilo YARP.",
    )
    app.state.client = httpx.AsyncClient(timeout=15)

    @app.on_event("shutdown")
    async def shutdown() -> None:
        await app.state.client.aclose()

    @app.get("/api/gateway/routes")
    async def list_routes() -> dict:
        return {"routes": ROUTES, "clusters": CLUSTERS}

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def proxy(path: str, request: Request) -> Response:
        incoming_path = "/" + path
        route = _match_route(incoming_path)
        if route is None:
            return JSONResponse(
                status_code=404,
                media_type="application/problem+json",
                content={
                    "type": "about:blank",
                    "title": "Rota nao encontrada",
                    "status": 404,
                    "detail": f"Nenhum cluster configurado para {incoming_path}.",
                },
            )

        cluster = CLUSTERS[route["cluster_id"]]
        target_url = f"{cluster['destination'].rstrip('/')}{incoming_path}"
        proxied = await app.state.client.request(
            request.method,
            target_url,
            content=await request.body(),
            headers={key: value for key, value in request.headers.items() if key.lower() != "host"},
            params=request.query_params,
        )
        return Response(
            content=proxied.content,
            status_code=proxied.status_code,
            headers={key: value for key, value in proxied.headers.items() if key.lower() != "content-encoding"},
            media_type=proxied.headers.get("content-type"),
        )

    return app


def _match_route(path: str) -> dict | None:
    for route in ROUTES:
        if path.startswith(route["prefix"]):
            return route
    return None


app = create_app()
