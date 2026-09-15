"""Text extraction and chunking for uploaded documents."""

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}

TARGET_CHUNK_CHARS = 3000  # ~750 tokens
CHUNK_OVERLAP_CHARS = 400


@dataclass
class ChunkData:
    idx: int
    page: int
    text: str


def extract_pages(path: Path) -> list[tuple[int, str]]:
    """Return (page_number, text) pairs; non-PDF files count as one page."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(path)
        return [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]
    if suffix in SUPPORTED_EXTENSIONS:
        return [(1, path.read_text(encoding="utf-8", errors="replace"))]
    raise ValueError(f"Unsupported file type '{suffix}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}")


def chunk_pages(pages: list[tuple[int, str]]) -> list[ChunkData]:
    """Split full text into overlapping chunks, remembering the page each starts on."""
    full_text = ""
    boundaries: list[tuple[int, int]] = []  # (start_offset, page_number)
    for page_no, text in pages:
        boundaries.append((len(full_text), page_no))
        full_text += text + "\n"

    def page_of(offset: int) -> int:
        page = boundaries[0][1] if boundaries else 1
        for start, page_no in boundaries:
            if start <= offset:
                page = page_no
            else:
                break
        return page

    chunks: list[ChunkData] = []
    start = 0
    while start < len(full_text):
        end = min(start + TARGET_CHUNK_CHARS, len(full_text))
        if end < len(full_text):
            # Snap the cut to a paragraph or sentence break in the second half.
            window = full_text[start + TARGET_CHUNK_CHARS // 2 : end]
            snap = max(window.rfind("\n\n"), window.rfind(". "))
            if snap != -1:
                end = start + TARGET_CHUNK_CHARS // 2 + snap + 1
        text = full_text[start:end].strip()
        if text:
            chunks.append(ChunkData(idx=len(chunks), page=page_of(start), text=text))
        if end >= len(full_text):
            break
        start = max(end - CHUNK_OVERLAP_CHARS, start + 1)
    return chunks
