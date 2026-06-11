# Gestao de Pedidos em Python

Projeto demonstrativo em Python para cobrir a rubrica das aulas de arquitetura, testes, Docker,
microsservicos, mensageria, CQRS, cache e tempo real.

## Stack

- FastAPI para APIs REST, Swagger/OpenAPI automatico em `/docs` e `/openapi.json`.
- Clean Architecture por servico: `domain`, `application`, `infrastructure`, `api`.
- DDD com entidades, Value Object e Domain Event.
- pytest, pytest-asyncio, unittest.mock/pytest-mock e httpx/TestClient para testes.
- Docker multi-stage build e Docker Compose.
- API Gateway em FastAPI, com rotas/clusters em estilo YARP.
- RabbitMQ + aio-pika para mensageria.
- Redis para cache distribuido.
- WebSocket do FastAPI para tempo real.

> Adaptacao importante: YARP, xUnit.net, Moq, FluentAssertions, WebApplicationFactory,
> MassTransit e Polly sao tecnologias do ecossistema .NET. Neste projeto, os equivalentes em
> Python sao FastAPI/httpx/pytest, fakes/mocks de Python, assertivas do pytest, TestClient,
> aio-pika e retry/circuit breaker implementados no cliente HTTP.

## Estrutura

```text
services/
  pedidos/        API de pedidos: Clean Architecture, CQRS, cache, RabbitMQ, cliente HTTP resiliente
  catalogo/       API de catalogo: produtos e estoque
  notificacoes/   consumer RabbitMQ + WebSocket para tempo real
  gateway/        API Gateway em FastAPI roteando /api/pedidos e /api/produtos
tests/
  pedidos/        testes unitarios, integracao de API e exemplo com Testcontainers
docs/
  roteiro-apresentacao.md
```

## Como executar

```powershell
docker compose up -d --build
docker compose ps
docker compose logs -f pedidos-api
```

Servicos principais:

- Gateway: http://localhost:8080/docs
- Pedidos direto: http://localhost:8001/docs
- Catalogo direto: http://localhost:8002/docs
- Notificacoes: http://localhost:8003/docs
- RabbitMQ Management: http://localhost:15672

## Exemplos de chamadas

Criar pedido pelo gateway:

```powershell
$body = @{
  cliente_id = "11111111-1111-1111-1111-111111111111"
  itens = @(
    @{ produto_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"; quantidade = 2 }
  )
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/pedidos -ContentType "application/json" -Body $body
```

Listar pedidos:

```powershell
Invoke-RestMethod http://localhost:8080/api/pedidos
```

Consultar produtos:

```powershell
Invoke-RestMethod http://localhost:8080/api/produtos
```

## Como testar

Instale as dependencias localmente:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .[test]
pytest
```

Rodar exemplos com Testcontainers:

```powershell
$env:RUN_TESTCONTAINERS = "1"
pytest tests/pedidos/testcontainers_test.py
```

## Pontos para falar na apresentacao

Use [docs/roteiro-apresentacao.md](docs/roteiro-apresentacao.md). Ele mapeia cada item da
rubrica para arquivos concretos do projeto.

