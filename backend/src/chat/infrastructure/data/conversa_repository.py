"""ConversaRepository (equiv. OrderRepository.cs)"""
from typing import List, Optional
from sqlalchemy.orm import Session
from chat.application.ports.i_conversa_repository import IConversaRepository
from chat.domain.entities.conversa import Conversa
from chat.infrastructure.data.database import ConversaModel


class ConversaRepository(IConversaRepository):
    def __init__(self, db: Session):
        self._db = db

    def _to_entity(self, model: ConversaModel) -> Conversa:
        c = Conversa.__new__(Conversa)
        c.id, c.usuario_id, c.titulo = model.id, model.usuario_id, model.titulo
        c.criado_em, c.atualizado_em, c.mensagens = model.criado_em, model.atualizado_em, []
        return c

    def _to_model(self, e: Conversa) -> ConversaModel:
        return ConversaModel(id=e.id, usuario_id=e.usuario_id, titulo=e.titulo,
                             criado_em=e.criado_em, atualizado_em=e.atualizado_em)

    def buscar_por_id(self, conversa_id: str) -> Optional[Conversa]:
        m = self._db.query(ConversaModel).filter(ConversaModel.id == conversa_id).first()
        return self._to_entity(m) if m else None

    def listar_por_usuario(self, usuario_id: str) -> List[Conversa]:
        ms = self._db.query(ConversaModel).filter(ConversaModel.usuario_id == usuario_id).order_by(ConversaModel.atualizado_em.desc()).all()
        return [self._to_entity(m) for m in ms]

    def salvar(self, conversa: Conversa) -> Conversa:
        ex = self._db.query(ConversaModel).filter(ConversaModel.id == conversa.id).first()
        if ex:
            ex.titulo, ex.atualizado_em = conversa.titulo, conversa.atualizado_em
        else:
            self._db.add(self._to_model(conversa))
        self._db.commit()
        return conversa

    def deletar(self, conversa_id: str) -> None:
        m = self._db.query(ConversaModel).filter(ConversaModel.id == conversa_id).first()
        if m:
            self._db.delete(m)
            self._db.commit()
