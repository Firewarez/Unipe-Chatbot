"""Handler: BuscarConhecimentoHandler (equiv. GetOrderByIdHandler.cs)"""
from typing import List
from chat.application.use_cases.buscar_conhecimento.buscar_conhecimento_query import BuscarConhecimentoQuery
from chat.application.ports.i_vector_store_service import IVectorStoreService


class BuscarConhecimentoHandler:
    def __init__(self, vector_store_service: IVectorStoreService):
        self._vector_store = vector_store_service

    def handle(self, query: BuscarConhecimentoQuery) -> List[str]:
        return self._vector_store.buscar_similares(texto=query.pergunta, limite=query.limite)
