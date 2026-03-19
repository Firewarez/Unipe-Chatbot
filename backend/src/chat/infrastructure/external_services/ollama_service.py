"""OllamaService - Implementa IIAService usando Ollama local (llama3.2)."""
from typing import List
import ollama
from chat.application.ports.i_ia_service import IIAService
from chat.domain.value_objects.resposta_ia import RespostaIA

SYSTEM_PROMPT = """Você é o assistente virtual oficial do Centro Universitário UNIPÊ (João Pessoa - PB).
Responda SEMPRE em português brasileiro. Use apenas o CONTEXTO fornecido.
Se não souber, diga educadamente. Seja conciso e direto. Não invente informações.

CONTEXTO:
{contexto}
"""


class OllamaService(IIAService):
    def __init__(self, model_name: str = "llama3.2:1b"):
        self._model_name = model_name

    def gerar_resposta(self, pergunta: str, contexto: List[str]) -> RespostaIA:
        ctx = "\n---\n".join(contexto) if contexto else "Nenhum contexto disponível."
        try:
            resp = ollama.chat(model=self._model_name, messages=[
                {"role": "system", "content": SYSTEM_PROMPT.format(contexto=ctx)},
                {"role": "user", "content": pergunta},
            ])
            return RespostaIA(texto=resp["message"]["content"],
                              fontes=tuple(f"Documento {i+1}" for i in range(len(contexto))),
                              confianca=0.8 if contexto else 0.3)
        except Exception as e:
            return RespostaIA(texto=f"Erro ao processar: {e}", fontes=tuple(), confianca=0.0)
