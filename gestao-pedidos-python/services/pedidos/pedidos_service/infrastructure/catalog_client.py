import asyncio
import time
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

import httpx

from pedidos_service.application.commands import ProdutoCatalogo


class CircuitOpenError(Exception):
    pass


@dataclass
class CircuitBreaker:
    max_failures: int = 3
    reset_timeout_seconds: int = 30
    failures: int = 0
    opened_at: float | None = None

    def before_call(self) -> None:
        if self.opened_at is None:
            return
        if time.monotonic() - self.opened_at >= self.reset_timeout_seconds:
            self.failures = 0
            self.opened_at = None
            return
        raise CircuitOpenError("Circuit breaker aberto para o Catalogo.")

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.max_failures:
            self.opened_at = time.monotonic()


class CatalogoHttpClient:
    def __init__(
        self,
        base_url: str,
        client: httpx.AsyncClient | None = None,
        breaker: CircuitBreaker | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.AsyncClient(timeout=5)
        self.breaker = breaker or CircuitBreaker()

    async def obter_produto(self, produto_id: UUID) -> ProdutoCatalogo | None:
        self.breaker.before_call()

        for attempt in range(3):
            try:
                response = await self.client.get(f"{self.base_url}/api/produtos/{produto_id}")
                if response.status_code == 404:
                    self.breaker.record_success()
                    return None
                response.raise_for_status()
                data = response.json()
                self.breaker.record_success()
                return ProdutoCatalogo(
                    id=UUID(data["id"]),
                    nome=data["nome"],
                    preco=Decimal(str(data["preco"])),
                    estoque=int(data["estoque"]),
                )
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError):
                self.breaker.record_failure()
                if attempt == 2:
                    raise
                await asyncio.sleep(0.2 * (attempt + 1))

        return None

