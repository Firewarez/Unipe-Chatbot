import asyncio
import json
import os
from contextlib import suppress

from aio_pika import ExchangeType, IncomingMessage, connect_robust
from fastapi import FastAPI, WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict) -> None:
        disconnected: list[WebSocket] = []
        for websocket in self.active_connections:
            try:
                await websocket.send_json(message)
            except RuntimeError:
                disconnected.append(websocket)
        for websocket in disconnected:
            self.disconnect(websocket)


manager = ConnectionManager()
processed_events: set[str] = set()


def create_app() -> FastAPI:
    app = FastAPI(
        title="GestaoPedidos.Notificacoes",
        version="0.1.0",
        description="Consumer RabbitMQ e WebSocket para atualizacoes em tempo real.",
    )
    app.state.consumer_task = None

    @app.on_event("startup")
    async def startup() -> None:
        app.state.consumer_task = asyncio.create_task(consume_pedido_criado())

    @app.on_event("shutdown")
    async def shutdown() -> None:
        if app.state.consumer_task:
            app.state.consumer_task.cancel()
            with suppress(asyncio.CancelledError):
                await app.state.consumer_task

    @app.get("/api/notificacoes/health")
    async def health() -> dict:
        return {"status": "ok"}

    @app.websocket("/ws/notificacoes")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    return app


async def consume_pedido_criado() -> None:
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    while True:
        try:
            connection = await connect_robust(rabbitmq_url)
            async with connection:
                channel = await connection.channel()
                exchange = await channel.declare_exchange("pedidos.events", ExchangeType.TOPIC, durable=True)
                queue = await channel.declare_queue("notificacoes.pedido-criado", durable=True)
                await queue.bind(exchange, routing_key="pedido.criado")

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        await handle_message(message)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print(f"Falha no consumer RabbitMQ: {exc}")
            await asyncio.sleep(5)


async def handle_message(message: IncomingMessage) -> None:
    async with message.process():
        if message.message_id and message.message_id in processed_events:
            return
        payload = json.loads(message.body.decode("utf-8"))
        if message.message_id:
            processed_events.add(message.message_id)
        await manager.broadcast({"tipo": "pedido_criado", "dados": payload})


app = create_app()
