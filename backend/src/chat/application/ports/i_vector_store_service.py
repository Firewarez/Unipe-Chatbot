"""Port: IVectorStoreService"""
from abc import ABC, abstractmethod
from typing import List, Optional


class IVectorStoreService(ABC):
    @abstractmethod
    def buscar_similares(self, texto: str, limite: int = 5) -> List[str]: pass
    @abstractmethod
    def adicionar_documento(self, documento_id: str, conteudo: str, metadata: Optional[dict] = None) -> None: pass
