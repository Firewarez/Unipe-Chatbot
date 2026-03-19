"""ChatController - Equiv. OrdersController.cs. Endpoints FastAPI."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from chat.infrastructure.data.database import get_db
from chat.infrastructure.data.conversa_repository import ConversaRepository
from chat.infrastructure.data.mensagem_repository import MensagemRepository
from chat.infrastructure.external_services.ollama_service import OllamaService
from chat.infrastructure.external_services.chroma_service import ChromaDBService
from chat.application.use_cases.enviar_mensagem.enviar_mensagem_command import EnviarMensagemCommand
from chat.application.use_cases.enviar_mensagem.enviar_mensagem_handler import EnviarMensagemHandler
from chat.domain.entities.conversa import Conversa

router = APIRouter(prefix="/api/chat", tags=["Chat"])


# --- Pydantic Models (Request/Response) ---
class MensagemRequest(BaseModel):
    conversa_id: str
    conteudo: str
    usuario_id: str

class MensagemResponse(BaseModel):
    resposta: str
    fontes: list[str]
    confianca: float
    conversa_id: str

class ConversaRequest(BaseModel):
    usuario_id: str
    titulo: str = "Nova Conversa"

class ConversaResponse(BaseModel):
    id: str
    usuario_id: str
    titulo: str
    criado_em: str
    atualizado_em: str

class MensagemHistoricoResponse(BaseModel):
    id: str
    conteudo: str
    remetente: str
    timestamp: str


# --- Serviços singleton ---
_ollama_service = OllamaService(model_name="llama3.2:1b")
_chroma_service = ChromaDBService()


# --- Endpoints ---
@router.post("/mensagem", response_model=MensagemResponse)
def enviar_mensagem(request: MensagemRequest, db: Session = Depends(get_db)):
    try:
        cmd = EnviarMensagemCommand(conversa_id=request.conversa_id, conteudo=request.conteudo, usuario_id=request.usuario_id)
        cmd.validar()
        handler = EnviarMensagemHandler(
            conversa_repository=ConversaRepository(db), mensagem_repository=MensagemRepository(db),
            ia_service=_ollama_service, vector_store_service=_chroma_service,
        )
        resp = handler.handle(cmd)
        return MensagemResponse(resposta=resp.texto, fontes=list(resp.fontes), confianca=resp.confianca, conversa_id=request.conversa_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/conversa", response_model=ConversaResponse)
def criar_conversa(request: ConversaRequest, db: Session = Depends(get_db)):
    c = Conversa(usuario_id=request.usuario_id, titulo=request.titulo)
    ConversaRepository(db).salvar(c)
    return ConversaResponse(id=c.id, usuario_id=c.usuario_id, titulo=c.titulo,
                            criado_em=c.criado_em.isoformat(), atualizado_em=c.atualizado_em.isoformat())


@router.get("/conversa/{conversa_id}", response_model=ConversaResponse)
def buscar_conversa(conversa_id: str, db: Session = Depends(get_db)):
    c = ConversaRepository(db).buscar_por_id(conversa_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")
    return ConversaResponse(id=c.id, usuario_id=c.usuario_id, titulo=c.titulo,
                            criado_em=c.criado_em.isoformat(), atualizado_em=c.atualizado_em.isoformat())


@router.get("/conversas/{usuario_id}", response_model=list[ConversaResponse])
def listar_conversas(usuario_id: str, db: Session = Depends(get_db)):
    return [ConversaResponse(id=c.id, usuario_id=c.usuario_id, titulo=c.titulo,
                             criado_em=c.criado_em.isoformat(), atualizado_em=c.atualizado_em.isoformat())
            for c in ConversaRepository(db).listar_por_usuario(usuario_id)]


@router.get("/conversa/{conversa_id}/mensagens", response_model=list[MensagemHistoricoResponse])
def listar_mensagens(conversa_id: str, db: Session = Depends(get_db)):
    return [MensagemHistoricoResponse(id=m.id, conteudo=m.conteudo, remetente=m.remetente, timestamp=m.timestamp.isoformat())
            for m in MensagemRepository(db).listar_por_conversa(conversa_id)]
