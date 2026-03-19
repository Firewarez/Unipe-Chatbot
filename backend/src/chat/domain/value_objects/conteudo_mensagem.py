"""Value Object: ConteudoMensagem (equiv. OrderStatus.cs) - imutável"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ConteudoMensagem:
    texto: str
    tipo: str = "texto"
