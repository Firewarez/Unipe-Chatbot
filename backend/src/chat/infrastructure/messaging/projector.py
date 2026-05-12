import logging
from sqlalchemy.orm import Session
from datetime import datetime
from chat.infrastructure.data.database import ConversaModel, MensagemModel

logger = logging.getLogger(__name__)

class ChatProjector:
    def __init__(self, db: Session):
        self.db = db

    def projetar_mensagem(self, payload: dict):
        conversa_id = payload.get('conversa_id')
        conteudo = payload.get('conteudo')
        
        logger.info(f"Projetando mensagem para Conversa: {conversa_id}")

        nova_mensagem = MensagemModel(
            id=payload.get('mensagem_id'),
            conversa_id=conversa_id,
            conteudo=conteudo,
            remetente=payload.get('remetente'),
            timestamp=datetime.now()
        )
        self.db.add(nova_mensagem)

        conversa = self.db.query(ConversaModel).filter_by(id=conversa_id).first()
        if conversa:
            conversa.ultima_mensagem = conteudo
            conversa.atualizado_em = datetime.now()
        
        self.db.commit()