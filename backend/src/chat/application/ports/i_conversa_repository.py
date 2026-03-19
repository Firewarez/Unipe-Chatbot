"""Port: IConversaRepository (equiv. IOrderRepository.cs)"""
from abc import ABC, abstractmethod
from typing import List, Optional
from chat.domain.entities.conversa import Conversa


class IConversaRepository(ABC):
    @abstractmethod
    def buscar_por_id(self, conversa_id: str) -> Optional[Conversa]: pass
    @abstractmethod
    def listar_por_usuario(self, usuario_id: str) -> List[Conversa]: pass
    @abstractmethod
    def salvar(self, conversa: Conversa) -> Conversa: pass
    @abstractmethod
    def deletar(self, conversa_id: str) -> None: pass
