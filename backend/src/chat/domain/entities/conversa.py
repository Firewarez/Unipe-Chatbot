"""Entidade: Conversa (equiv. Order.cs)"""
import uuid
from datetime import datetime
from typing import List


class Conversa:
    def __init__(self, usuario_id: str, titulo: str = "Nova Conversa"):
        self.id: str = str(uuid.uuid4())
        self.usuario_id: str = usuario_id
        self.titulo: str = titulo
        self.criado_em: datetime = datetime.now()
        self.atualizado_em: datetime = datetime.now()
        self.mensagens: List = []

    def adicionar_mensagem(self, mensagem) -> None:
        self.mensagens.append(mensagem)
        self.atualizado_em = datetime.now()

    def atualizar_titulo(self, novo_titulo: str) -> None:
        self.titulo = novo_titulo
        self.atualizado_em = datetime.now()
