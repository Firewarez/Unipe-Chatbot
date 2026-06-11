from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


class CatalogoDomainError(Exception):
    pass


@dataclass(frozen=True)
class Produto:
    id: UUID
    nome: str
    preco: Decimal
    estoque: int

    def __post_init__(self) -> None:
        if not self.nome.strip():
            raise CatalogoDomainError("Produto deve ter nome.")
        if self.preco < 0:
            raise CatalogoDomainError("Preco nao pode ser negativo.")
        if self.estoque < 0:
            raise CatalogoDomainError("Estoque nao pode ser negativo.")

