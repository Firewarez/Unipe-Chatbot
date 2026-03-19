"""MensagemRepository"""
from typing import List
from sqlalchemy.orm import Session
from chat.application.ports.i_mensagem_repository import IMensagemRepository
from chat.domain.entities.mensagem import Mensagem
from chat.infrastructure.data.database import MensagemModel


class MensagemRepository(IMensagemRepository):
    def __init__(self, db: Session):
        self._db = db

    def _to_entity(self, m: MensagemModel) -> Mensagem:
        msg = Mensagem.__new__(Mensagem)
        msg.id, msg.conversa_id, msg.conteudo = m.id, m.conversa_id, m.conteudo
        msg.remetente, msg.timestamp = m.remetente, m.timestamp
        return msg

    def salvar(self, mensagem: Mensagem) -> Mensagem:
        self._db.add(MensagemModel(id=mensagem.id, conversa_id=mensagem.conversa_id,
                                    conteudo=mensagem.conteudo, remetente=mensagem.remetente, timestamp=mensagem.timestamp))
        self._db.commit()
        return mensagem

    def listar_por_conversa(self, conversa_id: str) -> List[Mensagem]:
        ms = self._db.query(MensagemModel).filter(MensagemModel.conversa_id == conversa_id).order_by(MensagemModel.timestamp.asc()).all()
        return [self._to_entity(m) for m in ms]
