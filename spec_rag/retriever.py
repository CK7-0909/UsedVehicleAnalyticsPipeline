from __future__ import annotations

from typing import Any
from sentence_transformers import SentenceTransformer

from .config import CHROMA_PATH, EMBEDDING_MODEL


def _load_model() -> Any:
    return SentenceTransformer(EMBEDDING_MODEL)


def _get_client() -> Any:
    try:
        import chromadb
    except Exception as e:  # pragma: no cover - import error handled at runtime
        raise ImportError(
            "chromadb is required for retriever operations but could not be imported"
        ) from e

    return chromadb.PersistentClient(path=CHROMA_PATH)


def _get_collection() -> Any:
    client = _get_client()
    return client.get_or_create_collection("car_specs")


def query_specs(query: str, n_results: int = 3) -> list[dict[str, Any]]:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string")
    if n_results <= 0:
        raise ValueError("n_results must be a positive integer")

    model = _load_model()
    embedding = model.encode([query])
    query_embedding = embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)
    collection = _get_collection()
    response = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    documents = response.get("documents", [[]])[0]
    metadatas = response.get("metadatas", [[]])[0]
    distances = response.get("distances", [[]])[0]

    return [
        {
            "document": document,
            "metadata": metadata,
            "distance": distance,
        }
        for document, metadata, distance in zip(documents, metadatas, distances)
    ]
