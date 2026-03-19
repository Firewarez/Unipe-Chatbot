# API do ChatBot UNIPÊ - Guia para o Frontend

Base URL: `http://localhost:8000`

Documentação interativa (Swagger): `http://localhost:8000/docs`

---

## Autenticação

Não há autenticação por enquanto. Todas as rotas são abertas.

---

## Rotas

### 1. Enviar mensagem (principal)

```
POST /api/chat/mensagem
```

Envia a mensagem do usuário e retorna a resposta da IA.

**Request:**
```json
{
  "conversa_id": "string (UUID da conversa)",
  "conteudo": "string (texto da mensagem)",
  "usuario_id": "string (identificador do usuário)"
}
```

**Response 200:**
```json
{
  "resposta": "O UNIPÊ oferece cursos de Engenharia Civil, Computação...",
  "fontes": ["Documento 1", "Documento 2"],
  "confianca": 0.8,
  "conversa_id": "mesmo ID enviado"
}
```

**Response 400:** conteúdo vazio ou dados inválidos  
**Response 500:** erro interno (IA indisponível, etc.)

> ⚠️ Essa rota pode demorar alguns segundos dependendo do modelo de IA.

---

### 2. Criar conversa

```
POST /api/chat/conversa
```

Cria uma nova sessão de conversa. Sempre crie uma conversa antes de enviar mensagens.

**Request:**
```json
{
  "usuario_id": "string",
  "titulo": "string (opcional, default: 'Nova Conversa')"
}
```

**Response 200:**
```json
{
  "id": "uuid-gerado",
  "usuario_id": "string",
  "titulo": "Nova Conversa",
  "criado_em": "2026-03-19T15:00:00",
  "atualizado_em": "2026-03-19T15:00:00"
}
```

---

### 3. Buscar conversa por ID

```
GET /api/chat/conversa/{conversa_id}
```

**Response 200:** objeto da conversa (mesmo formato acima)  
**Response 404:** conversa não encontrada

---

### 4. Listar conversas de um usuário

```
GET /api/chat/conversas/{usuario_id}
```

Retorna um array de conversas, ordenadas da mais recente para a mais antiga.

**Response 200:**
```json
[
  { "id": "...", "usuario_id": "...", "titulo": "...", "criado_em": "...", "atualizado_em": "..." },
  { "id": "...", "usuario_id": "...", "titulo": "...", "criado_em": "...", "atualizado_em": "..." }
]
```

---

### 5. Ver histórico de mensagens

```
GET /api/chat/conversa/{conversa_id}/mensagens
```

Retorna todas as mensagens de uma conversa em ordem cronológica.

**Response 200:**
```json
[
  {
    "id": "uuid",
    "conteudo": "Quais cursos existem?",
    "remetente": "usuario",
    "timestamp": "2026-03-19T15:00:00"
  },
  {
    "id": "uuid",
    "conteudo": "O UNIPÊ oferece mais de 100 cursos...",
    "remetente": "bot",
    "timestamp": "2026-03-19T15:00:02"
  }
]
```

> O campo `remetente` é sempre `"usuario"` ou `"bot"`.

---

### 6. Health check

```
GET /health
```

**Response:** `{ "status": "healthy" }`

---

## Fluxo sugerido no frontend

1. Ao abrir o chat, crie uma conversa com `POST /api/chat/conversa`
2. Guarde o `id` retornado
3. Para cada mensagem do usuário, envie `POST /api/chat/mensagem` com o `conversa_id`
4. Mostre a `resposta` retornada como mensagem do bot
5. Para recarregar o histórico, use `GET /api/chat/conversa/{id}/mensagens`
6. Para listar as conversas anteriores, use `GET /api/chat/conversas/{usuario_id}`

---

## CORS

O backend aceita requisições de `http://localhost:3000` e `http://127.0.0.1:3000`.
