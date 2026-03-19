"""Testes de Application - EnviarMensagemHandler (com mocks)."""
from unittest.mock import MagicMock
import pytest
from chat.application.use_cases.enviar_mensagem.enviar_mensagem_command import EnviarMensagemCommand
from chat.application.use_cases.enviar_mensagem.enviar_mensagem_handler import EnviarMensagemHandler
from chat.domain.entities.conversa import Conversa
from chat.domain.value_objects.resposta_ia import RespostaIA


class TestEnviarMensagemHandler:
    def _mocks(self):
        return MagicMock(), MagicMock(), MagicMock(), MagicMock()

    def test_conversa_existente(self):
        cr, mr, ia, vs = self._mocks()
        c = Conversa(usuario_id="u1", titulo="Existe"); c.id = "c1"
        cr.buscar_por_id.return_value = c
        vs.buscar_similares.return_value = ["Contexto"]
        ia.gerar_resposta.return_value = RespostaIA(texto="Resp", fontes=("F1",), confianca=0.8)

        r = EnviarMensagemHandler(cr, mr, ia, vs).handle(
            EnviarMensagemCommand(conversa_id="c1", conteudo="Pergunta?", usuario_id="u1"))
        assert r.texto == "Resp" and mr.salvar.call_count == 2

    def test_cria_conversa_nova(self):
        cr, mr, ia, vs = self._mocks()
        cr.buscar_por_id.return_value = None
        vs.buscar_similares.return_value = []
        ia.gerar_resposta.return_value = RespostaIA(texto="Olá!", confianca=0.3)

        EnviarMensagemHandler(cr, mr, ia, vs).handle(
            EnviarMensagemCommand(conversa_id="new", conteudo="Oi", usuario_id="u1"))
        assert cr.salvar.call_count == 2

    def test_sem_contexto(self):
        cr, mr, ia, vs = self._mocks()
        c = Conversa(usuario_id="u1"); c.id = "c1"
        cr.buscar_por_id.return_value = c
        vs.buscar_similares.return_value = []
        ia.gerar_resposta.return_value = RespostaIA(texto="Sem info", confianca=0.3)

        r = EnviarMensagemHandler(cr, mr, ia, vs).handle(
            EnviarMensagemCommand(conversa_id="c1", conteudo="Preço?", usuario_id="u1"))
        assert r.confianca == 0.3


class TestCommand:
    def test_vazio(self):
        with pytest.raises(ValueError):
            EnviarMensagemCommand(conversa_id="c", conteudo="", usuario_id="u").validar()

    def test_valido(self):
        EnviarMensagemCommand(conversa_id="c", conteudo="Oi", usuario_id="u").validar()
