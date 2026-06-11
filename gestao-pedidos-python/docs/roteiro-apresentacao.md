# Roteiro de apresentacao

## 1. Fundamentos arquiteturais e API Design

- Mostrar que cada servico tem as camadas `domain`, `application`, `infrastructure` e `api`.
- Em `pedidos_service/domain/entities.py`, apontar:
  - `Pedido` como Entidade;
  - `Money` como Value Object;
  - `PedidoCriadoEvent` como Domain Event.
- Explicar os Bounded Contexts:
  - `Pedidos`: ciclo de vida do pedido;
  - `Catalogo`: produtos e estoque;
  - `Notificacoes`: comunicacao em tempo real.
- Abrir `/docs` para demonstrar Swagger/OpenAPI.
- Mostrar URIs RESTful:
  - `GET /api/pedidos`;
  - `POST /api/pedidos`;
  - `GET /api/pedidos/{pedido_id}`;
  - `PUT /api/pedidos/{pedido_id}/status`;
  - `DELETE /api/pedidos/{pedido_id}`.
- Mostrar `api/errors.py`, que retorna erro padronizado no formato Problem Details.

## 2. Qualidade de Software e testes automatizados

- Explicar a Piramide de Testes:
  - muitos testes unitarios para regras de dominio e handlers;
  - alguns testes de integracao para endpoints;
  - poucos testes E2E em fluxo completo.
- Mostrar `tests/pedidos/test_criar_pedido.py`:
  - testa o handler sem subir API;
  - usa dublês/fakes para repositorio, catalogo e publicador.
- Mostrar `tests/pedidos/test_pedidos_api.py`:
  - usa `TestClient`, equivalente Python ao teste de API isolado.
- Mostrar `tests/pedidos/testcontainers_test.py`:
  - exemplo de Testcontainers com Redis.

## 3. Docker e containerizacao

- Abrir qualquer Dockerfile, por exemplo `services/pedidos/Dockerfile`.
- Explicar o multi-stage build:
  - estagio `builder`: baixa dependencias e gera wheels;
  - estagio `runtime`: imagem final mais enxuta.
- Abrir `docker-compose.yml` e mostrar:
  - API Gateway;
  - Pedidos;
  - Catalogo;
  - Notificacoes;
  - SQL Server;
  - RabbitMQ;
  - Redis.
- Mostrar `depends_on` com healthcheck e volumes nomeados:
  - `sqlserver-data`;
  - `rabbitmq-data`;
  - `redis-data`.
- Explicar rede Docker:
  - `pedidos-api` acessa `catalogo-api` pelo hostname `catalogo-api`;
  - `pedidos-api` acessa RabbitMQ pelo hostname `rabbitmq`.
- Demonstrar comandos:
  - `docker compose up -d --build`;
  - `docker compose ps`;
  - `docker compose logs -f pedidos-api`.

## 4. Microsservicos, HTTP resiliente e API Gateway

- Mostrar a separacao dos servicos em pastas independentes em `services/`.
- Em `pedidos_service/infrastructure/catalog_client.py`, mostrar:
  - cliente HTTP reutilizavel com `httpx.AsyncClient`;
  - retry para falhas transitorias;
  - circuit breaker para evitar falha em cascata.
- Em `services/gateway/gateway_service/routes.json` e `main.py`, mostrar:
  - rotas por prefixo;
  - clusters internos;
  - `/api/pedidos` roteando para Pedidos;
  - `/api/produtos` roteando para Catalogo.
- Explicar CAP:
  - com microsservicos e mensageria, o sistema privilegia disponibilidade;
  - alguns dados de leitura podem ficar eventualmente consistentes.

## 5. Mensageria, CQRS, cache e tempo real

- Em `pedidos_service/domain/events.py`, mostrar `PedidoCriadoEvent`.
- Em `pedidos_service/infrastructure/message_bus.py`, mostrar publicacao no RabbitMQ.
- Em `notificacoes_service/main.py`, mostrar consumer assinando evento `pedido.criado`.
- Explicar exchanges:
  - Direct: roteia por routing key exata;
  - Fanout: entrega para todas as filas ligadas;
  - Topic: roteia por padroes como `pedido.*`.
- Explicar idempotencia:
  - RabbitMQ entrega ao menos uma vez;
  - o consumer registra eventos processados para nao repetir efeito.
- Em `pedidos_service/application/commands.py` e `queries.py`, mostrar CQRS:
  - Commands para escrita e regras de dominio;
  - Queries para leitura otimizada.
- Em `pedidos_service/infrastructure/queries.py`, mostrar leitura via SQL textual, equivalente a consulta enxuta no estilo Dapper.
- Em `pedidos_service/infrastructure/cache.py`, mostrar cache-aside com TTL usando Redis.
- Em `notificacoes_service/main.py`, mostrar WebSocket em `/ws/notificacoes` para atualizacoes em tempo real.
