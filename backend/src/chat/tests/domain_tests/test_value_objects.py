"""Testes de Domínio - Value Objects (imutabilidade + igualdade)."""
import pytest
from chat.domain.value_objects.conteudo_mensagem import ConteudoMensagem
from chat.domain.value_objects.resposta_ia import RespostaIA


class TestConteudoMensagem:
    def test_criar(self):
        assert ConteudoMensagem(texto="Oi").tipo == "texto"

    def test_igualdade(self):
        assert ConteudoMensagem(texto="A") == ConteudoMensagem(texto="A")

    def test_desigualdade(self):
        assert ConteudoMensagem(texto="A") != ConteudoMensagem(texto="B")

    def test_imutavel(self):
        with pytest.raises(AttributeError):
            ConteudoMensagem(texto="A").texto = "X"


class TestRespostaIA:
    def test_criar(self):
        r = RespostaIA(texto="R", fontes=("F",), confianca=0.9)
        assert r.confianca == 0.9

    def test_padrao(self):
        r = RespostaIA(texto="X")
        assert r.fontes == tuple() and r.confianca == 0.0

    def test_igualdade(self):
        assert RespostaIA(texto="A", confianca=0.5) == RespostaIA(texto="A", confianca=0.5)

    def test_imutavel(self):
        with pytest.raises(AttributeError):
            RespostaIA(texto="A").texto = "X"
