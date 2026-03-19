"""Testes de Domínio - Entidades."""
import pytest
from chat.domain.entities.conversa import Conversa
from chat.domain.entities.mensagem import Mensagem
from chat.domain.entities.conhecimento import Conhecimento


class TestConversa:
    def test_criar(self):
        c = Conversa(usuario_id="u1", titulo="Teste")
        assert c.usuario_id == "u1" and c.titulo == "Teste" and c.id is not None

    def test_titulo_padrao(self):
        assert Conversa(usuario_id="u1").titulo == "Nova Conversa"

    def test_adicionar_mensagem(self):
        c = Conversa(usuario_id="u1")
        c.adicionar_mensagem(Mensagem(conversa_id=c.id, conteudo="Oi", remetente="usuario"))
        assert len(c.mensagens) == 1

    def test_atualizar_titulo(self):
        c = Conversa(usuario_id="u1")
        c.atualizar_titulo("Novo")
        assert c.titulo == "Novo"

    def test_ids_unicos(self):
        assert Conversa(usuario_id="u1").id != Conversa(usuario_id="u1").id


class TestMensagem:
    def test_criar_usuario(self):
        m = Mensagem(conversa_id="c1", conteudo="Olá", remetente="usuario")
        assert m.remetente == "usuario" and m.id is not None

    def test_criar_bot(self):
        assert Mensagem(conversa_id="c1", conteudo="Resp", remetente="bot").remetente == "bot"

    def test_remetente_invalido(self):
        with pytest.raises(ValueError):
            Mensagem(conversa_id="c1", conteudo="X", remetente="admin")

    def test_ids_unicos(self):
        m1 = Mensagem(conversa_id="c1", conteudo="A", remetente="usuario")
        m2 = Mensagem(conversa_id="c1", conteudo="B", remetente="usuario")
        assert m1.id != m2.id


class TestConhecimento:
    def test_criar(self):
        d = Conhecimento(titulo="T", conteudo="C", fonte="F", categoria="K")
        assert d.titulo == "T" and d.id is not None

    def test_ids_unicos(self):
        d1 = Conhecimento(titulo="A", conteudo="B", fonte="C", categoria="D")
        d2 = Conhecimento(titulo="A", conteudo="B", fonte="C", categoria="D")
        assert d1.id != d2.id
