# 🤖 UNIPÊ ChatBot

Um chatbot inteligente feito para responder dúvidas sobre o **Centro Universitário UNIPÊ** de João Pessoa - PB. Ele funciona como um FAQ automatizado: alunos, vestibulandos ou qualquer pessoa interessada pode perguntar sobre cursos, valores, horários, infraestrutura, vestibular, bolsas e muito mais.

O chatbot entende a pergunta, busca as informações mais relevantes na base de dados e gera uma resposta em linguagem natural usando inteligência artificial — tudo rodando localmente, sem depender de serviços pagos na nuvem.

---

## 💡 Como funciona?

Quando uma pessoa envia uma mensagem para o chatbot, acontecem os seguintes passos:

1. **Recebe a pergunta** — O frontend envia a mensagem do usuário para o backend via API.
2. **Salva a mensagem** — A pergunta é guardada no banco de dados para manter o histórico da conversa.
3. **Busca informações relevantes** — O sistema procura na base de conhecimento os trechos de texto que mais se relacionam com a pergunta. Essa busca é feita por similaridade semântica (ou seja, ele entende o significado, não apenas palavras exatas).
4. **Gera a resposta com IA** — Os trechos encontrados são enviados junto com a pergunta para o modelo de IA (Llama 3.2), que gera uma resposta em português combinando o contexto com a pergunta.
5. **Devolve a resposta** — A resposta é salva no banco e enviada de volta para o frontend, onde o usuário a visualiza no chat.

Esse processo é chamado de **RAG** (Retrieval-Augmented Generation): a IA não inventa respostas, ela sempre consulta a base de dados antes de responder.

---

## 🛠️ Tecnologias

| Componente | Tecnologia | Para que serve |
|---|---|---|
| **Backend** | Python + FastAPI | Servidor que recebe e processa as requisições |
| **Frontend** | React + Vite | Interface do chat onde o usuário conversa |
| **Banco de dados** | SQLite + SQLAlchemy | Guarda conversas e mensagens |
| **Banco vetorial** | ChromaDB | Armazena o conhecimento e faz busca por similaridade |
| **IA / LLM** | Ollama + Llama 3.2 | Gera as respostas em linguagem natural |
| **Testes** | Pytest | Garante que tudo funciona como esperado |

---

## 📁 Estrutura do projeto

```
ChatBot/
├── frontend/           → Interface do chat (React)
├── backend/
│   ├── src/chat/
│   │   ├── api/        → Endpoints da API (recebe as requisições HTTP)
│   │   ├── application/ → Lógica dos casos de uso (enviar mensagem, buscar conhecimento)
│   │   ├── domain/     → Regras do negócio (entidades, validações)
│   │   ├── infrastructure/ → Conexões externas (banco, IA, ChromaDB)
│   │   └── tests/      → Testes unitários e de integração
│   ├── conftest.py     → Configuração do pytest
│   └── requirements.txt → Dependências Python
└── data/
    └── unipe_knowledge.json → Base de conhecimento sobre a UNIPÊ
```

---

## 🚀 Como rodar o projeto

### Pré-requisitos

- Python 3.10 ou superior
- Node.js 18 ou superior
- Ollama instalado ([baixar aqui](https://ollama.com/download))

### 1. Instalar o modelo de IA

Depois de instalar o Ollama, abra o terminal e baixe o modelo:

```bash
ollama pull llama3.2:1b
```

### 2. Instalar as dependências do backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. Alimentar a base de conhecimento

Esse comando lê o arquivo `data/unipe_knowledge.json` e carrega todas as informações no ChromaDB:

```bash
cd backend
$env:PYTHONPATH="src"; python -m chat.infrastructure.data_loader.seed_knowledge
```

Sempre que você adicionar novas informações no JSON, rode esse comando novamente para atualizar a base.

### 4. Iniciar o backend

```bash
cd backend
$env:PYTHONPATH="src"; uvicorn chat.api.main:app --reload --port 8000
```

O servidor inicia em `http://localhost:8000`. Acesse `http://localhost:8000/docs` para ver a documentação interativa da API (Swagger).

### 5. Iniciar o frontend

```bash
cd frontend
npm install
npm run dev
```

O frontend roda em `http://localhost:3000`.

---

## 📡 Rotas da API

O backend expõe as seguintes rotas. Todas começam com `/api/chat`:

### Enviar mensagem

```
POST /api/chat/mensagem
```

Envia uma mensagem do usuário e recebe a resposta gerada pela IA.

**Corpo da requisição:**
```json
{
  "conversa_id": "id-da-conversa",
  "conteudo": "Quais cursos de engenharia o UNIPÊ oferece?",
  "usuario_id": "usuario-123"
}
```

**Resposta:**
```json
{
  "resposta": "O UNIPÊ oferece os cursos de Engenharia Civil, Engenharia de Computação, Engenharia Elétrica e Engenharia de Produção. Todos possuem laboratórios equipados e parcerias com empresas para estágios.",
  "fontes": ["Documento 1", "Documento 2"],
  "confianca": 0.8,
  "conversa_id": "id-da-conversa"
}
```

### Criar conversa

```
POST /api/chat/conversa
```

Cria uma nova sessão de conversa.

**Corpo:** `{ "usuario_id": "usuario-123", "titulo": "Dúvidas sobre cursos" }`  
**Resposta:** retorna o objeto da conversa criada com `id`, `titulo`, `criado_em` e `atualizado_em`.

### Buscar conversa

```
GET /api/chat/conversa/{conversa_id}
```

Retorna os dados de uma conversa específica. Retorna 404 se não existir.

### Listar conversas de um usuário

```
GET /api/chat/conversas/{usuario_id}
```

Retorna a lista de todas as conversas do usuário, ordenadas da mais recente para a mais antiga.

### Ver histórico de mensagens

```
GET /api/chat/conversa/{conversa_id}/mensagens
```

Retorna todas as mensagens de uma conversa (tanto do usuário quanto do bot), em ordem cronológica.

### Health check

```
GET /health
```

Retorna `{ "status": "healthy" }` — serve para verificar se o servidor está rodando.

---

## 📚 Como adicionar conteúdo à IA

A base de conhecimento fica no arquivo `data/unipe_knowledge.json`. Cada entrada representa um bloco de informação que a IA pode consultar:

```json
{
  "titulo": "Nome descritivo do assunto",
  "conteudo": "Texto completo com todas as informações. Quanto mais detalhado, melhor a IA responde.",
  "fonte": "De onde veio essa informação (ex: site oficial, instagram, edital)",
  "categoria": "Uma palavra-chave para organizar (ex: cursos, financeiro, vestibular)"
}
```

**Dicas para boas entradas:**

- Escreva o conteúdo como se fosse uma resposta pronta. A IA usa esse texto diretamente para formular a resposta.
- Inclua dados concretos: valores, datas, nomes, horários, endereços.
- Separe os assuntos em entradas diferentes. É melhor ter 10 entradas focadas do que 1 entrada gigante.
- Depois de editar o JSON, rode o comando de seed novamente:

```bash
cd backend
python -m chat.infrastructure.data_loader.seed_knowledge
```

---

## 🧪 Testes

O projeto possui testes unitários e de integração. Para rodar todos:

```bash
cd backend
python -m pytest src/chat/tests/ -v
```

Os testes cobrem:

- **Entidades** — Verifica se Conversa, Mensagem e Conhecimento são criados corretamente, se os IDs são únicos e se as validações funcionam.
- **Value Objects** — Testa que os objetos de valor (como RespostaIA) são imutáveis e comparados por conteúdo.
- **Handlers** — Simula o envio de mensagem completo (com repositórios e IA simulados) para garantir que o fluxo funciona sem depender de serviços externos.
- **API** — Testa os endpoints HTTP de verdade, criando conversas, enviando mensagens e verificando as respostas.

---

## 👥 Equipe

Projeto desenvolvido como **Projeto Integrador** do curso do Centro Universitário UNIPÊ.
