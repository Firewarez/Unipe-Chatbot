"""Port: IMensagemRepository"""
from abc import ABC, abstractmethod
from typing import List
from chat.domain.entities.mensagem import Mensagem


class IMensagemRepository(ABC):
    @abstractmethod
    def salvar(self, mensagem: Mensagem) -> Mensagem: pass
    @abstractmethod
    def listar_por_conversa(self, conversa_id: str) -> List[Mensagem]: pass
