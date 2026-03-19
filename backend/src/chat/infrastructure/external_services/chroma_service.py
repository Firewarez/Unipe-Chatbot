"""ChromaDBService - Implementa IVectorStoreService para busca semântica."""
from typing import List, Optional
import chromadb
from chat.application.ports.i_vector_store_service import IVectorStoreService


class ChromaDBService(IVectorStoreService):
    def __init__(self, collection_name: str = "unipe_knowledge", persist_directory: str = "./chroma_data"):
        self._client = chromadb.PersistentClient(path=persist_directory)
        self._collection = self._client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})

    def buscar_similares(self, texto: str, limite: int = 5) -> List[str]:
        if self._collection.count() == 0:
            return []
        docs = self._collection.query(query_texts=[texto], n_results=min(limite, self._collection.count()))
        return docs.get("documents", [[]])[0]

    def adicionar_documento(self, documento_id: str, conteudo: str, metadata: Optional[dict] = None) -> None:
        self._collection.upsert(ids=[documento_id], documents=[conteudo], metadatas=[metadata] if metadata else None)

    def contar_documentos(self) -> int:
        return self._collection.count()
