"""Map-reduce summarization: short docs in one call, long docs in batches."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import Chunk, Document
from .usage import run_chat

SINGLE_CALL_CHAR_LIMIT = 12000
MAP_BATCH_CHAR_LIMIT = 12000
MAX_MAP_BATCHES = 10

SYSTEM = (
    "You are a reading assistant that summarizes documents faithfully. "
    "Capture the main argument, key points, and important details. "
    "Use short paragraphs and bullet points where helpful."
)


def summarize_document(
    session: Session, document: Document, provider_name: str, model: str | None
) -> dict:
    texts = list(
        session.scalars(
            select(Chunk.text).where(Chunk.document_id == document.id).order_by(Chunk.idx)
        )
    )
    if not texts:
        raise ValueError("Document has no extracted text to summarize.")

    batches: list[str] = []
    current = ""
    for text in texts:
        if current and len(current) + len(text) > MAP_BATCH_CHAR_LIMIT:
            batches.append(current)
            current = ""
        current += text + "\n\n"
    if current:
        batches.append(current)

    truncated = len(batches) > MAX_MAP_BATCHES
    batches = batches[:MAX_MAP_BATCHES]

    calls = 0
    if len(batches) == 1:
        prompt = (
            f"Summarize the following document, '{document.title}':\n\n{batches[0]}"
        )
        logged = run_chat(
            session,
            provider_name,
            [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
            model,
            feature="summarize",
        )
        summary = logged.result.text
        calls = 1
    else:
        partials = []
        for i, batch in enumerate(batches):
            prompt = (
                f"This is part {i + 1} of {len(batches)} of the document "
                f"'{document.title}'. Summarize this part:\n\n{batch}"
            )
            logged = run_chat(
                session,
                provider_name,
                [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                model,
                feature="summarize",
            )
            partials.append(logged.result.text)
            calls += 1
        combined = "\n\n".join(
            f"Part {i + 1} summary:\n{p}" for i, p in enumerate(partials)
        )
        prompt = (
            f"Combine these part summaries of the document '{document.title}' into "
            f"one coherent overall summary:\n\n{combined}"
        )
        logged = run_chat(
            session,
            provider_name,
            [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
            model,
            feature="summarize",
        )
        summary = logged.result.text
        calls += 1

    return {
        "summary": summary,
        "truncated": truncated,
        "llm_calls": calls,
        "provider": logged.provider,
        "model": logged.result.model,
    }
