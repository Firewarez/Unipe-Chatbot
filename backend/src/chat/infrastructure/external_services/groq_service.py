"""IIAService usando Groq API em modo OpenAI-compatible."""
import os
from typing import List

import httpx

from chat.application.ports.i_ia_service import IIAService
from chat.domain.value_objects.resposta_ia import RespostaIA


SYSTEM_PROMPT = """Você é o assistente virtual do Centro Universitário UNIPÊ.
Responda em português brasileiro.
Use apenas o CONTEXTO fornecido.
Se a informação não estiver no CONTEXTO, diga que não encontrou na base carregada.
Não invente valores, datas, duração, bolsas ou contatos.
Seja direto e organize a resposta em bullets quando ajudar.

CONTEXTO:
{contexto}
"""


class GroqService(IIAService):
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        self._model_name = model_name
        self._api_key = os.getenv("GROQ_API_KEY", "")
        self._base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    def gerar_resposta(self, pergunta: str, contexto: List[str]) -> RespostaIA:
        if not self._api_key:
            return RespostaIA(
                texto="GROQ_API_KEY não configurada. Configure a chave no Render ou use IA_PROVIDER=demo.",
                fontes=tuple(),
                confianca=0.0,
            )

        ctx = "\n---\n".join(contexto) if contexto else "Nenhum contexto disponível."
        payload = {
            "model": self._model_name,
            "temperature": 0.1,
            "top_p": 0.8,
            "max_tokens": 600,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT.format(contexto=ctx)},
                {"role": "user", "content": pergunta},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=30) as client:
                resposta = client.post(f"{self._base_url}/chat/completions", json=payload, headers=headers)
                resposta.raise_for_status()
            data = resposta.json()
            texto = data["choices"][0]["message"]["content"]
            return RespostaIA(
                texto=texto,
                fontes=tuple(f"Documento {i+1}" for i in range(len(contexto))),
                confianca=0.85 if contexto else 0.35,
            )
        except Exception as exc:
            return RespostaIA(
                texto=f"Erro ao chamar Groq: {exc}. Para a apresentação, use IA_PROVIDER=demo como fallback.",
                fontes=tuple(),
                confianca=0.0,
            )
