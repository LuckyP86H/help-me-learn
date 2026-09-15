"""SQLite persistence: documents, chunks (with embedding vectors), usage log."""

from collections.abc import Iterator
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, LargeBinary, Text, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from .config import settings


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str]
    title: Mapped[str]
    stored_path: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    num_pages: Mapped[int] = mapped_column(default=0)
    num_chars: Mapped[int] = mapped_column(default=0)
    # Which embedder indexed this document; queries must use the same one.
    embedder_name: Mapped[str] = mapped_column(default="")

    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    idx: Mapped[int]
    page: Mapped[int]
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[bytes] = mapped_column(LargeBinary)  # float32 array bytes

    document: Mapped[Document] = relationship(back_populates="chunks")


class UsageLog(Base):
    __tablename__ = "usage_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    provider: Mapped[str]
    model: Mapped[str]
    feature: Mapped[str]  # chat | summarize | qa | embed
    input_tokens: Mapped[int] = mapped_column(default=0)
    output_tokens: Mapped[int] = mapped_column(default=0)
    latency_ms: Mapped[int] = mapped_column(default=0)


_engine = None
_session_factory = None


def get_engine():
    global _engine
    if _engine is None:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(
            f"sqlite:///{settings.db_path}", connect_args={"check_same_thread": False}
        )
    return _engine


def init_db() -> None:
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(get_engine())


def get_session() -> Iterator[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    session = _session_factory()
    try:
        yield session
    finally:
        session.close()
