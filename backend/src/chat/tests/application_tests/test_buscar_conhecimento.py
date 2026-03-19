"""Testes - BuscarConhecimentoHandler."""
from unittest.mock import MagicMock
from chat.application.use_cases.buscar_conhecimento.buscar_conhecimento_query import BuscarConhecimentoQuery
from chat.application.use_cases.buscar_conhecimento.buscar_conhecimento_handler import BuscarConhecimentoHandler


class TestBuscarConhecimento:
    def test_com_resultados(self):
        vs = MagicMock()
        vs.buscar_similares.return_value = ["Doc1", "Doc2"]
        assert len(BuscarConhecimentoHandler(vs).handle(BuscarConhecimentoQuery(pergunta="Direito"))) == 2

    def test_sem_resultados(self):
        vs = MagicMock()
        vs.buscar_similares.return_value = []
        assert len(BuscarConhecimentoHandler(vs).handle(BuscarConhecimentoQuery(pergunta="???"))) == 0
