"""Integration events for chat messages."""
from dataclasses import dataclass, field
from .integration_event import IntegrationEvent


@dataclass(frozen=True)
class MensagemEnviadaEvent(IntegrationEvent):
    conversa_id: str
    usuario_id: str
    mensagem_id: str
    conteudo: str
    remetente: str
    timestamp: str
    event_type: str = field(default="mensagem_enviada", init=False)


@dataclass(frozen=True)
class RespostaGeradaEvent(IntegrationEvent):
    conversa_id: str
    usuario_id: str
    mensagem_id: str
    conteudo: str
    remetente: str
    confianca: float
    fontes: list[str]
    timestamp: str
    event_type: str = field(default="resposta_gerada", init=False)
