"""Servico de resposta para demo sem dependencia de LLM externo."""
from typing import List

from chat.application.ports.i_ia_service import IIAService
from chat.domain.value_objects.resposta_ia import RespostaIA


class DemoIAService(IIAService):
    def gerar_resposta(self, pergunta: str, contexto: List[str]) -> RespostaIA:
        trechos = [trecho.strip() for trecho in contexto if trecho and trecho.strip()]
        if not trechos:
            return RespostaIA(
                texto=(
                    "Nao encontrei essa informacao na base carregada do UNIPE. "
                    "Tente perguntar sobre cursos, bolsas, atendimento, biblioteca ou servicos."
                ),
                fontes=tuple(),
                confianca=0.2,
            )

        resposta = [
            "Encontrei estas informacoes na base oficial carregada:",
            "",
        ]
        for indice, trecho in enumerate(trechos[:3], start=1):
            resposta.append(f"{indice}. {self._resumir_trecho(trecho)}")

        resposta.append("")
        resposta.append("Consulte a fonte original para confirmar detalhes como valores, vagas e datas.")
        return RespostaIA(
            texto="\n".join(resposta),
            fontes=tuple(f"Documento {i+1}" for i in range(len(trechos[:3]))),
            confianca=0.7,
        )

    def _resumir_trecho(self, trecho: str, limite: int = 650) -> str:
        texto = " ".join(trecho.split())
        if len(texto) <= limite:
            return texto

        corte = texto[:limite].rsplit(".", 1)[0].strip()
        if len(corte) < 180:
            corte = texto[:limite].strip()
        return f"{corte}."
