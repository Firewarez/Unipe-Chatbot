"""seed_knowledge.py - Carrega dados da UNIPÊ de unipe_knowledge.json no ChromaDB.

Uso:
  cd backend
  $env:PYTHONPATH="src"; python -m chat.infrastructure.data_loader.seed_knowledge
"""
import json
import os

from chat.infrastructure.external_services.chroma_service import ChromaDBService


def carregar_conhecimento():
    # Navega de backend/ (CWD) para ChatBot/data/unipe_knowledge.json
    json_path = os.path.normpath(os.path.join(os.getcwd(), "..", "data", "unipe_knowledge.json"))
    if not os.path.exists(json_path):
        print(f"Erro: {json_path} não encontrado.")
        print("Certifique-se de rodar este comando a partir da pasta backend/")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    print(f"Carregando {len(docs)} documentos no ChromaDB...")
    chroma = ChromaDBService()
    for i, doc in enumerate(docs):
        chroma.adicionar_documento(
            documento_id=f"unipe_{doc['categoria']}_{i}",
            conteudo=f"{doc['titulo']}\n\n{doc['conteudo']}",
            metadata={"titulo": doc["titulo"], "fonte": doc["fonte"], "categoria": doc["categoria"]},
        )
        print(f"  [{i+1}/{len(docs)}] {doc['titulo']}")
    print(f"\nSucesso! {chroma.contar_documentos()} documentos carregados.")


if __name__ == "__main__":
    carregar_conhecimento()
