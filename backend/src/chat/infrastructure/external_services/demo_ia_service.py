"""Servico de resposta para demo sem dependencia de LLM externo."""
import re
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

        bullets = self._montar_bullets(pergunta, trechos)
        resposta = [self._introducao(pergunta), ""]
        for bullet in bullets:
            resposta.append(f"- {bullet}")

        resposta.append("")
        resposta.append("Para valores, vagas, datas e regras, confirme na pagina oficial antes de tomar decisao.")
        return RespostaIA(
            texto="\n".join(resposta),
            fontes=tuple(f"Documento {i+1}" for i in range(min(len(trechos), 3))),
            confianca=0.7,
        )

    def _introducao(self, pergunta: str) -> str:
        if "atendimento" in pergunta.lower():
            return "Sobre atendimento do UNIPE, encontrei:"
        if "biblioteca" in pergunta.lower():
            return "Sobre a biblioteca do UNIPE, encontrei:"
        if "bolsa" in pergunta.lower() or "financiamento" in pergunta.lower() or "prouni" in pergunta.lower():
            return "Sobre bolsas e financiamentos, encontrei:"
        if "curso" in pergunta.lower() or "gradua" in pergunta.lower():
            return "Sobre esse curso no UNIPE, encontrei:"
        return "Encontrei estas informacoes na base oficial carregada:"

    def _montar_bullets(self, pergunta: str, trechos: List[str]) -> List[str]:
        termos = self._termos_relevantes(pergunta)
        candidatos: list[tuple[int, str]] = []
        for trecho in trechos:
            for frase in self._frases_limpas(trecho):
                score = self._score_frase(frase, termos)
                if score > 0:
                    candidatos.append((score, frase))

        if not candidatos:
            candidatos = [(1, self._resumir_trecho(trecho)) for trecho in trechos[:3]]

        vistos: set[str] = set()
        bullets: list[str] = []
        for _, frase in sorted(candidatos, key=lambda item: item[0], reverse=True):
            chave = frase.lower()
            if chave in vistos:
                continue
            vistos.add(chave)
            bullets.append(frase)
            if len(bullets) == 4:
                break
        return bullets

    def _frases_limpas(self, trecho: str) -> List[str]:
        texto = self._limpar_texto(trecho)
        frases = re.split(r"(?<=[.!?])\s+", texto)
        return [
            frase.strip()
            for frase in frases
            if 45 <= len(frase.strip()) <= 280 and not self._eh_ruido(frase)
        ]

    def _score_frase(self, frase: str, termos: set[str]) -> int:
        frase_lower = frase.lower()
        score = sum(frase_lower.count(termo) for termo in termos)
        if self._eh_ruido(frase):
            score -= 5
        if any(marcador in frase_lower for marcador in ("telefone", "0800", "e-mail", "email", "app duda", "caa")):
            score += 2
        if any(marcador in frase_lower for marcador in ("duração", "semestres", "anos", "modalidade")):
            score += 1
        return score

    def _termos_relevantes(self, pergunta: str) -> set[str]:
        stopwords = {
            "sobre", "quais", "qual", "como", "para", "com", "dos", "das", "uma",
            "curso", "cursos", "unipe", "unipê", "oferece", "informacoes", "informações",
        }
        termos = {
            termo
            for termo in re.findall(r"[a-zA-ZÀ-ÿ0-9]{3,}", pergunta.lower())
            if termo not in stopwords
        }
        pergunta_lower = pergunta.lower()
        if "atendimento" in pergunta_lower:
            termos.update({"atendimento", "duda", "caa", "telefone", "email", "0800", "aluno"})
        if "computação" in pergunta_lower or "computacao" in pergunta_lower:
            termos.update({"computação", "computacao", "tecnologia", "software", "programação"})
        if "direito" in pergunta_lower:
            termos.update({"direito", "jurídica", "juridica", "oab", "estágio", "estagio"})
        return termos

    def _limpar_texto(self, texto: str) -> str:
        texto = re.sub(r"!\[[^\]]*]\([^)]+\)", "", texto)
        texto = re.sub(r"\[([^\]]+)]\([^)]+\)", r"\1", texto)
        texto = re.sub(r"[*_#`]+", "", texto)
        texto = re.sub(r"\b[\wÀ-ÿ |:,.!?-]+ - Parte \d+\s*", "", texto)
        texto = re.sub(r"\s+", " ", texto)
        return texto.strip()

    def _eh_ruido(self, texto: str) -> bool:
        texto_lower = texto.lower()
        termos_ruido = (
            "cookies", "política de privacidade", "política de cookies", "visto confere",
            "certidão de nascimento", "imprimir comprovante", "preferências", "suplência",
            "supletivo", "firma reconhecida", "aceitar os cookies",
        )
        return any(termo in texto_lower for termo in termos_ruido)

    def _resumir_trecho(self, trecho: str, limite: int = 360) -> str:
        texto = self._limpar_texto(trecho)
        if len(texto) <= limite:
            return texto

        corte = texto[:limite].rsplit(".", 1)[0].strip()
        if len(corte) < 180:
            corte = texto[:limite].strip()
        return f"{corte}."
