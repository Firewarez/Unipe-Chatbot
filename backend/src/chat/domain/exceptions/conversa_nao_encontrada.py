"""Exceção: ConversaNaoEncontradaException (equiv. OrderNotFoundException.cs)"""


class ConversaNaoEncontradaException(Exception):
    def __init__(self, conversa_id: str):
        self.conversa_id = conversa_id
        super().__init__(f"Conversa '{conversa_id}' não encontrada.")
