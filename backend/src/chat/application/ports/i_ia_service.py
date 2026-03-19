"""Port: IIAService"""
from abc import ABC, abstractmethod
from typing import List
from chat.domain.value_objects.resposta_ia import RespostaIA


class IIAService(ABC):
    @abstractmethod
    def gerar_resposta(self, pergunta: str, contexto: List[str]) -> RespostaIA: pass
