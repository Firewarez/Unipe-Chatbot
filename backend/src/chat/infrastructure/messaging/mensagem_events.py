from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class MensagemEnviadaEvent:
    conversa_id: str
    usuario_id: str
    mensagem_id: str
    conteudo: str
    remetente: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RespostaGeradaEvent:
    conversa_id: str
    mensagem_id: str
    conteudo: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)