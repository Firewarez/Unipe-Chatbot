"""Command: EnviarMensagemCommand (equiv. CreateOrderCommand.cs)"""
from dataclasses import dataclass


@dataclass
class EnviarMensagemCommand:
    conversa_id: str
    conteudo: str
    usuario_id: str

    def validar(self) -> None:
        if not self.conteudo or not self.conteudo.strip():
            raise ValueError("O conteúdo da mensagem não pode ser vazio.")
        if not self.conversa_id or not self.conversa_id.strip():
            raise ValueError("O ID da conversa é obrigatório.")
        if not self.usuario_id or not self.usuario_id.strip():
            raise ValueError("O ID do usuário é obrigatório.")
