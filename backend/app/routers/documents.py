import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import Document, get_session
from ..services.documents import SUPPORTED_EXTENSIONS, chunk_pages, extract_pages
from ..services.indexing import index_chunks
from ..services.qa import ask_document
from ..services.summarize import summarize_document

router = APIRouter(prefix="/api", tags=["documents"])

MAX_UPLOAD_BYTES = 50 * 1024 * 1024


class LLMSelection(BaseModel):
    provider: str
    model: str | None = None


class AskRequest(LLMSelection):
    question: str


def _doc_info(doc: Document, num_chunks: int | None = None) -> dict:
    info = {
        "id": doc.id,
        "filename": doc.filename,
        "title": doc.title,
        "created_at": doc.created_at.isoformat(),
        "num_pages": doc.num_pages,
        "num_chars": doc.num_chars,
        "embedder": doc.embedder_name,
    }
    if num_chunks is not None:
        info["num_chunks"] = num_chunks
    return info


def _get_document(session: Session, document_id: int) -> Document:
    doc = session.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    return doc


@router.post("/documents")
async def upload_document(file: UploadFile, session: Session = Depends(get_session)) -> dict:
    suffix = Path(file.filename or "upload").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}",
        )
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 50 MB limit")

    stored = settings.uploads_dir / f"{uuid.uuid4().hex}{suffix}"
    stored.write_bytes(content)

    try:
        pages = extract_pages(stored)
    except Exception as e:
        stored.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Could not extract text: {e}")

    total_chars = sum(len(text) for _page, text in pages)
    if total_chars == 0:
        stored.unlink(missing_ok=True)
        raise HTTPException(
            status_code=422,
            detail="No extractable text found (scanned PDFs need OCR, which isn't supported yet).",
        )

    doc = Document(
        filename=file.filename or stored.name,
        title=Path(file.filename or stored.name).stem,
        stored_path=str(stored),
        num_pages=len(pages),
        num_chars=total_chars,
    )
    session.add(doc)
    session.commit()

    try:
        num_chunks = index_chunks(session, doc, chunk_pages(pages))
    except Exception as e:
        session.delete(doc)
        session.commit()
        stored.unlink(missing_ok=True)
        raise HTTPException(status_code=502, detail=f"Embedding failed: {e}")

    return _doc_info(doc, num_chunks)


@router.get("/documents")
def list_documents(session: Session = Depends(get_session)) -> list[dict]:
    docs = session.scalars(select(Document).order_by(Document.created_at.desc())).all()
    return [_doc_info(d, len(d.chunks)) for d in docs]


@router.delete("/documents/{document_id}")
def delete_document(document_id: int, session: Session = Depends(get_session)) -> dict:
    doc = _get_document(session, document_id)
    Path(doc.stored_path).unlink(missing_ok=True)
    session.delete(doc)
    session.commit()
    return {"deleted": document_id}


@router.post("/documents/{document_id}/summarize")
def summarize(
    document_id: int, req: LLMSelection, session: Session = Depends(get_session)
) -> dict:
    doc = _get_document(session, document_id)
    try:
        return summarize_document(session, doc, req.provider, req.model)
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e.args[0]))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider error: {e}")


@router.post("/documents/{document_id}/ask")
def ask(document_id: int, req: AskRequest, session: Session = Depends(get_session)) -> dict:
    doc = _get_document(session, document_id)
    try:
        return ask_document(session, doc, req.provider, req.model, req.question)
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e.args[0]))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider error: {e}")
