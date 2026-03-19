"""Entidade: Conhecimento (base RAG)"""
import uuid
from datetime import datetime


class Conhecimento:
    def __init__(self, titulo: str, conteudo: str, fonte: str, categoria: str):
        self.id: str = str(uuid.uuid4())
        self.titulo: str = titulo
        self.conteudo: str = conteudo
        self.fonte: str = fonte
        self.categoria: str = categoria
        self.criado_em: datetime = datetime.now()
