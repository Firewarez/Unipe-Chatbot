"""Integration events for chat messages."""
from dataclasses import dataclass, field
from typing import List
from .integration_event import IntegrationEvent


@dataclass(frozen=True)
class MensagemEnviadaEvent(IntegrationEvent):
    conversa_id: str = ""
    usuario_id: str = ""
    mensagem_id: str = ""
    conteudo: str = ""
    remetente: str = ""
    timestamp: str = ""
    event_type: str = field(default="mensagem_enviada", init=False)


@dataclass(frozen=True)
class RespostaGeradaEvent(IntegrationEvent):
    conversa_id: str = ""
    usuario_id: str = ""
    mensagem_id: str = ""
    conteudo: str = ""
    remetente: str = ""
    confianca: float = 0.0
    fontes: List[str] = field(default_factory=list)
    timestamp: str = ""
    event_type: str = field(default="resposta_generated", init=False)