from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ProdutoResponse(BaseModel):
    id: UUID
    nome: str
    preco: Decimal
    estoque: int

