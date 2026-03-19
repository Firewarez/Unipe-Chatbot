"""Handler: EnviarMensagemHandler (equiv. CreateOrderHandler.cs)
Pipeline RAG: salvar msg → buscar contexto → IA gera resposta → salvar resposta.
"""
from chat.application.use_cases.enviar_mensagem.enviar_mensagem_command import EnviarMensagemCommand
from chat.application.ports.i_conversa_repository import IConversaRepository
from chat.application.ports.i_mensagem_repository import IMensagemRepository
from chat.application.ports.i_ia_service import IIAService
from chat.application.ports.i_vector_store_service import IVectorStoreService
from chat.domain.entities.mensagem import Mensagem
from chat.domain.entities.conversa import Conversa
from chat.domain.value_objects.resposta_ia import RespostaIA


class EnviarMensagemHandler:
    def __init__(self, conversa_repository: IConversaRepository, mensagem_repository: IMensagemRepository,
                 ia_service: IIAService, vector_store_service: IVectorStoreService):
        self._conversa_repo = conversa_repository
        self._mensagem_repo = mensagem_repository
        self._ia_service = ia_service
        self._vector_store = vector_store_service

    def handle(self, command: EnviarMensagemCommand) -> RespostaIA:
        conversa = self._conversa_repo.buscar_por_id(command.conversa_id)
        if conversa is None:
            conversa = Conversa(usuario_id=command.usuario_id)
            conversa.id = command.conversa_id
            self._conversa_repo.salvar(conversa)

        self._mensagem_repo.salvar(Mensagem(conversa_id=command.conversa_id, conteudo=command.conteudo, remetente="usuario"))
        contexto = self._vector_store.buscar_similares(texto=command.conteudo, limite=3)
        resposta = self._ia_service.gerar_resposta(pergunta=command.conteudo, contexto=contexto)
        self._mensagem_repo.salvar(Mensagem(conversa_id=command.conversa_id, conteudo=resposta.texto, remetente="bot"))

        if conversa.titulo == "Nova Conversa":
            conversa.atualizar_titulo(command.conteudo[:50] + "..." if len(command.conteudo) > 50 else command.conteudo)
            self._conversa_repo.salvar(conversa)

        return resposta
