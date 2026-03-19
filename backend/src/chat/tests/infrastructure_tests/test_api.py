"""Testes de API - Endpoints FastAPI."""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from chat.api.main import app
from chat.infrastructure.data.database import Base, get_db
from chat.domain.value_objects.resposta_ia import RespostaIA

test_engine = create_engine("sqlite:///./test_chatbot.db", connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


class TestHealth:
    def test_root(self):
        assert client.get("/").json()["status"] == "online"

    def test_health(self):
        assert client.get("/health").json()["status"] == "healthy"


class TestConversa:
    def test_criar(self):
        r = client.post("/api/chat/conversa", json={"usuario_id": "u1", "titulo": "T"})
        assert r.status_code == 200 and r.json()["titulo"] == "T"

    def test_buscar_existente(self):
        cid = client.post("/api/chat/conversa", json={"usuario_id": "u1"}).json()["id"]
        assert client.get(f"/api/chat/conversa/{cid}").status_code == 200

    def test_buscar_inexistente(self):
        assert client.get("/api/chat/conversa/xxx").status_code == 404

    def test_listar(self):
        client.post("/api/chat/conversa", json={"usuario_id": "u1"})
        client.post("/api/chat/conversa", json={"usuario_id": "u1"})
        assert len(client.get("/api/chat/conversas/u1").json()) == 2


class TestMensagem:
    @patch("chat.api.controllers.chat_controller._ollama_service")
    @patch("chat.api.controllers.chat_controller._chroma_service")
    def test_enviar_mock(self, mock_chroma, mock_ollama):
        mock_chroma.buscar_similares.return_value = ["Ctx"]
        mock_ollama.gerar_resposta.return_value = RespostaIA(texto="Mock", fontes=("F",), confianca=0.9)
        cid = client.post("/api/chat/conversa", json={"usuario_id": "u1"}).json()["id"]
        r = client.post("/api/chat/mensagem", json={"conversa_id": cid, "conteudo": "Curso?", "usuario_id": "u1"})
        assert r.status_code == 200

    def test_vazio(self):
        assert client.post("/api/chat/mensagem", json={"conversa_id": "c", "conteudo": "", "usuario_id": "u"}).status_code == 400
