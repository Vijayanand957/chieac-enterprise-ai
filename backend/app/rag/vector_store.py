"""Thin wrapper around a local Chroma vector store using sentence-transformers
embeddings. Swappable for pgvector/Azure AI Search in production by implementing
the same interface (add_chunks / similarity_search).
"""
from __future__ import annotations

import chromadb
from chromadb.utils import embedding_functions

from app.config import get_settings

settings = get_settings()

_client = chromadb.PersistentClient(path=settings.vector_store_dir)
_embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=settings.embedding_model
)
_collection = _client.get_or_create_collection(
    name="org_documents",
    embedding_function=_embedder,
    metadata={"hnsw:space": "cosine"},
)


def add_chunks(doc_id: str, filename: str, chunks: list[str]) -> int:
    """Embed and persist chunks for one document. Returns chunk count."""
    if not chunks:
        return 0
    ids = [f"{doc_id}::{i}" for i in range(len(chunks))]
    metadatas = [{"doc_id": doc_id, "filename": filename, "chunk_index": i} for i in range(len(chunks))]
    _collection.add(ids=ids, documents=chunks, metadatas=metadatas)
    return len(chunks)


def similarity_search(query: str, k: int = 5) -> list[dict]:
    """Return top-k chunks with their source filename and similarity distance."""
    if _collection.count() == 0:
        return []
    results = _collection.query(query_texts=[query], n_results=min(k, _collection.count()))
    hits = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        hits.append({"text": doc, "filename": meta.get("filename"), "score": 1 - dist})
    return hits


def delete_document(doc_id: str) -> None:
    _collection.delete(where={"doc_id": doc_id})
