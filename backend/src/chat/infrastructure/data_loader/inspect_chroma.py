"""Inspeciona documentos carregados no ChromaDB.

Uso:
  cd backend
  $env:PYTHONPATH="src"; python -m chat.infrastructure.data_loader.inspect_chroma
  $env:PYTHONPATH="src"; python -m chat.infrastructure.data_loader.inspect_chroma --query "direito"
  $env:PYTHONPATH="src"; python -m chat.infrastructure.data_loader.inspect_chroma --export ../data/chroma_export.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from chat.infrastructure.external_services.chroma_service import ChromaDBService


def _preview(texto: str, tamanho: int = 500) -> str:
    texto = " ".join(texto.split())
    return texto[:tamanho] + ("..." if len(texto) > tamanho else "")


def listar(chroma: ChromaDBService, limite: int) -> None:
    dados = chroma.listar_documentos(limite=limite)
    print(f"Total no ChromaDB: {chroma.contar_documentos()}")
    for indice, item in enumerate(dados, start=1):
        metadata = item.get("metadata") or {}
        print(f"\n[{indice}] {metadata.get('titulo', 'Sem titulo')}")
        print(f"Fonte: {metadata.get('fonte', 'Sem fonte')}")
        print(f"Categoria: {metadata.get('categoria', 'sem-categoria')}")
        print(_preview(item.get("documento", "")))


def buscar(chroma: ChromaDBService, query: str, limite: int) -> None:
    resultados = chroma.buscar_similares(texto=query, limite=limite)
    print(f"Resultados para: {query}")
    for indice, documento in enumerate(resultados, start=1):
        print(f"\n[{indice}]")
        print(_preview(documento, tamanho=900))


def exportar(chroma: ChromaDBService, destino: str) -> None:
    dados = chroma.listar_documentos(limite=chroma.contar_documentos())
    path = Path(destino)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exportado: {path.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspeciona a base ChromaDB do chatbot.")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--query", help="Busca semantica para testar recuperacao.")
    parser.add_argument("--export", help="Exporta documentos e metadados para JSON.")
    args = parser.parse_args()

    chroma = ChromaDBService()
    if args.export:
        exportar(chroma, args.export)
    elif args.query:
        buscar(chroma, query=args.query, limite=args.limit)
    else:
        listar(chroma, limite=args.limit)


if __name__ == "__main__":
    main()
