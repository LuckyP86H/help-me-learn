"""Embed document chunks on upload and persist the vectors."""

import numpy as np
from sqlalchemy.orm import Session

from ..db import Chunk, Document
from ..providers.registry import get_embedder
from .documents import ChunkData
from .usage import log_usage

EMBED_BATCH_SIZE = 128


def index_chunks(session: Session, document: Document, chunks: list[ChunkData]) -> int:
    embedder = get_embedder()
    document.embedder_name = embedder.name

    for batch_start in range(0, len(chunks), EMBED_BATCH_SIZE):
        batch = chunks[batch_start : batch_start + EMBED_BATCH_SIZE]
        vectors = embedder.embed([c.text for c in batch])
        for chunk, vector in zip(batch, vectors):
            session.add(
                Chunk(
                    document_id=document.id,
                    idx=chunk.idx,
                    page=chunk.page,
                    text=chunk.text,
                    embedding=np.asarray(vector, dtype=np.float32).tobytes(),
                )
            )
        if embedder.name != "mock":
            # Embedding APIs don't come back through run_chat, so log here.
            approx_tokens = sum(len(c.text) // 4 for c in batch)
            log_usage(
                session,
                provider=embedder.name,
                model=getattr(embedder, "embedding_model", "embedding"),
                feature="embed",
                input_tokens=approx_tokens,
                output_tokens=0,
                latency_ms=0,
            )
    session.commit()
    return len(chunks)


def embed_query(text: str) -> np.ndarray:
    vector = get_embedder().embed([text])[0]
    return np.asarray(vector, dtype=np.float32)
