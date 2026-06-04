# Observabilidade (Prometheus + Grafana)

## 1) Subir backend local
No terminal do projeto:

```powershell
cd backend
$env:PYTHONPATH="src"
uvicorn chat.api.main:app --reload --port 8000
```

## 2) Subir stack de observabilidade
Em outro terminal, na raiz do projeto:

```powershell
docker compose -f docker-compose.observability.yml up -d
```

## 3) Validar endpoints

```powershell
curl http://localhost:8000/metrics
curl http://localhost:9090/-/healthy
```

## 4) Abrir Grafana
- URL: http://localhost:3001
- Usuário: `admin`
- Senha: `admin`
- Dashboard provisionado: `ChatBot Observabilidade` (pasta `ChatBot`)

## 5) Gerar tráfego para popular gráficos

```powershell
for ($i = 0; $i -lt 15; $i++) {
  Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/chat/conversa" -ContentType "application/json" -Body '{"usuario_id":"u1","titulo":"obs"}' | Out-Null
  Start-Sleep -Milliseconds 400
}
```

## 6) Tirar print para a atividade
Capture uma única imagem contendo:
- URL do Grafana (`http://localhost:3001`)
- Dashboard `ChatBot Observabilidade`
- Os 3 painéis com dados:
  - `HTTP Requests por Segundo`
  - `Latência Média HTTP`
  - `Eventos de Negócio por Segundo`
- Intervalo de tempo em `Last 15 minutes`

Dica: use `Win + Shift + S` para captura retangular em tela cheia.
