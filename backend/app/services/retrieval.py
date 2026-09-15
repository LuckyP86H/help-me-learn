"""Cosine top-k retrieval over a document's stored chunk vectors."""

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import Chunk, Document
from ..providers.registry import get_embedder
from .indexing import embed_query

TOP_K = 6


def top_k_chunks(
    session: Session, document: Document, query: str, k: int = TOP_K
) -> list[tuple[Chunk, float]]:
    embedder = get_embedder()
    if document.embedder_name and document.embedder_name != embedder.name:
        raise ValueError(
            f"Document was indexed with the '{document.embedder_name}' embedder but "
            f"'{embedder.name}' is active. Re-upload the document or restore "
            f"EMBEDDING_PROVIDER={document.embedder_name}."
        )

    chunks = list(
        session.scalars(
            select(Chunk).where(Chunk.document_id == document.id).order_by(Chunk.idx)
        )
    )
    if not chunks:
        return []

    matrix = np.stack([np.frombuffer(c.embedding, dtype=np.float32) for c in chunks])
    query_vec = embed_query(query)
    norms = np.linalg.norm(matrix, axis=1) * (np.linalg.norm(query_vec) or 1.0)
    norms[norms == 0] = 1.0
    similarities = (matrix @ query_vec) / norms
    order = np.argsort(-similarities)[:k]
    return [(chunks[i], float(similarities[i])) for i in order]
