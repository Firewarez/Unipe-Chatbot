"""Restaura documentos no ChromaDB a partir de um export JSON.

Uso:
  cd backend
  $env:PYTHONPATH="src"; python -m chat.infrastructure.data_loader.import_chroma_export --input ../data/chroma_export.json
"""
from __future__ import annotations

import argparse
import json

from chat.infrastructure.external_services.chroma_service import ChromaDBService


def importar(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        dados = json.load(f)

    chroma = ChromaDBService()
    chroma.limpar_documentos()

    for item in dados:
        documento = item.get("documento")
        if not isinstance(documento, str) or not documento.strip():
            continue
        chroma.adicionar_documento(
            documento_id=item["id"],
            conteudo=documento,
            metadata=item.get("metadata") or {},
        )

    print(f"Sucesso! {chroma.contar_documentos()} documentos/blocos restaurados.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Restaura um export JSON no ChromaDB.")
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    importar(args.input)


if __name__ == "__main__":
    main()
