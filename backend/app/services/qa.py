"""RAG question answering: retrieve top-k chunks, answer with citations."""

from sqlalchemy.orm import Session

from ..db import Document
from .retrieval import top_k_chunks
from .usage import run_chat

SYSTEM = (
    "You are a reading assistant. Answer the question using ONLY the numbered "
    "excerpts provided. Cite the excerpts you used as [1], [2], etc. If the "
    "excerpts don't contain the answer, say so plainly instead of guessing."
)

SNIPPET_CHARS = 300


def ask_document(
    session: Session,
    document: Document,
    provider_name: str,
    model: str | None,
    question: str,
) -> dict:
    hits = top_k_chunks(session, document, question)
    if not hits:
        raise ValueError("Document has no indexed content to search.")

    excerpts = "\n\n".join(
        f"[{i + 1}] (page {chunk.page})\n{chunk.text}"
        for i, (chunk, _score) in enumerate(hits)
    )
    prompt = (
        f"Excerpts from '{document.title}':\n\n{excerpts}\n\n"
        f"Question: {question}"
    )
    logged = run_chat(
        session,
        provider_name,
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
        model,
        feature="qa",
    )
    citations = [
        {
            "n": i + 1,
            "page": chunk.page,
            "score": round(score, 4),
            "snippet": chunk.text[:SNIPPET_CHARS],
        }
        for i, (chunk, score) in enumerate(hits)
    ]
    return {
        "answer": logged.result.text,
        "citations": citations,
        "provider": logged.provider,
        "model": logged.result.model,
        "latency_ms": logged.latency_ms,
    }
