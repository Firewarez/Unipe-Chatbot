"""Query: BuscarConhecimentoQuery (equiv. GetOrderByIdQuery.cs)"""
from dataclasses import dataclass


@dataclass
class BuscarConhecimentoQuery:
    pergunta: str
    limite: int = 5
