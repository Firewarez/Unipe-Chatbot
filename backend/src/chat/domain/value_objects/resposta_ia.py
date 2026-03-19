"""Value Object: RespostaIA - resposta gerada pela IA com fontes e confiança"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RespostaIA:
    texto: str
    fontes: tuple = field(default_factory=tuple)
    confianca: float = 0.0
