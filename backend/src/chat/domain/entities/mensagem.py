"""Entidade: Mensagem (equiv. OrderItem.cs)"""
import uuid
from datetime import datetime


class Mensagem:
    def __init__(self, conversa_id: str, conteudo: str, remetente: str):
        if remetente not in ("usuario", "bot"):
            raise ValueError("Remetente deve ser 'usuario' ou 'bot'.")
        self.id: str = str(uuid.uuid4())
        self.conversa_id: str = conversa_id
        self.conteudo: str = conteudo
        self.remetente: str = remetente
        self.timestamp: datetime = datetime.now()
