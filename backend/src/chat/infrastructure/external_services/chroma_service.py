"""ChromaDBService - Implementa IVectorStoreService para busca semântica."""
from pathlib import Path
import re
from typing import Any, List, Optional

import chromadb
from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2
from chat.application.ports.i_vector_store_service import IVectorStoreService


class ChromaDBService(IVectorStoreService):
    def __init__(self, collection_name: str = "unipe_knowledge", persist_directory: str = "./chroma_data"):
        self._configurar_cache_embeddings(persist_directory)
        self._client = chromadb.PersistentClient(path=persist_directory)
        self._collection = self._client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})

    def _configurar_cache_embeddings(self, persist_directory: str) -> None:
        base_dir = Path(persist_directory).resolve().parent
        ONNXMiniLM_L6_V2.DOWNLOAD_PATH = base_dir / "chroma_onnx_cache" / ONNXMiniLM_L6_V2.MODEL_NAME

    def buscar_similares(self, texto: str, limite: int = 5) -> List[str]:
        if self._collection.count() == 0:
            return []
        n_results = min(max(limite * 4, limite), self._collection.count())
        resultado = self._collection.query(query_texts=[texto], n_results=n_results)
        documentos = [doc for doc in resultado.get("documents", [[]])[0] if isinstance(doc, str) and doc.strip()]
        return self._reordenar_por_termos(texto, documentos)[:limite]

    def _reordenar_por_termos(self, texto: str, documentos: List[str]) -> List[str]:
        termos = self._termos_relevantes(texto)
        if not termos:
            return documentos

        def score(item: tuple[int, str]) -> tuple[int, int]:
            indice, documento = item
            doc_lower = documento.lower()
            matches = sum(doc_lower.count(termo) for termo in termos)
            penalty = self._penalidade_ruido(doc_lower)
            return matches - penalty, -indice

        return [doc for _, doc in sorted(enumerate(documentos), key=score, reverse=True)]

    def _penalidade_ruido(self, texto: str) -> int:
        termos_ruido = {
            "cookies", "política de cookies", "política de privacidade", "visto confere",
            "certidão de nascimento", "imprimir comprovante", "preferências",
            "suplência", "supletivo", "firma reconhecida",
        }
        return sum(2 for termo in termos_ruido if termo in texto)

    def _termos_relevantes(self, texto: str) -> set[str]:
        stopwords = {
            "sobre", "quais", "qual", "como", "para", "com", "dos", "das", "uma",
            "curso", "cursos", "unipe", "unipê", "graduacao", "graduação",
        }
        termos = {
            termo
            for termo in re.findall(r"[a-zA-ZÀ-ÿ0-9]{3,}", texto.lower())
            if termo not in stopwords
        }
        if "ads" in texto.lower():
            termos.update({"analise", "análise", "desenvolvimento", "sistemas"})
        if "atendimento" in texto.lower():
            termos.update({"caa", "duda", "telefone", "email", "aluno", "ex-alunos", "0800"})
        return termos

    def adicionar_documento(self, documento_id: str, conteudo: str, metadata: Optional[dict] = None) -> None:
        self._collection.upsert(ids=[documento_id], documents=[conteudo], metadatas=[metadata] if metadata else None)

    def limpar_documentos(self) -> None:
        documentos = self._collection.get()
        ids = documentos.get("ids", [])
        if ids:
            self._collection.delete(ids=ids)

    def listar_documentos(self, limite: int = 10) -> List[dict[str, Any]]:
        dados = self._collection.get(limit=limite, include=["documents", "metadatas"])
        ids = dados.get("ids", [])
        documentos = dados.get("documents", [])
        metadatas = dados.get("metadatas", [])
        return [
            {"id": doc_id, "documento": documento, "metadata": metadata}
            for doc_id, documento, metadata in zip(ids, documentos, metadatas)
        ]

    def contar_documentos(self) -> int:
        return self._collection.count()
