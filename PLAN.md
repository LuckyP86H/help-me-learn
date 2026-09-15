# PLAN — help-me-learn

## Vision

A personal agent that helps me learn faster: upload books/articles, get summaries and
grounded answers, and understand my own AI usage — **without being tied to any one LLM
vendor**. Start with one core use case (reading assistance), keep the architecture clean
enough to grow.

## Guiding principles

- **LLM-agnostic**: every model call goes through a small adapter interface
  (`LLMProvider` / `EmbeddingProvider`). Adding a provider = one new adapter file.
- **Runs with zero keys**: a Mock provider makes the full app testable offline; real keys
  live only in `backend/.env` (gitignored), placeholders in `.env.example`.
- **Everything measured**: every LLM call is logged (provider, model, feature, tokens,
  latency) and visible on the dashboard.
- **Start small, scale later**: SQLite + numpy cosine similarity now; the retrieval
  interface allows swapping in a real vector store later without touching callers.

## Milestones (v1)

- [x] **M1 — Scaffold + docs**: monorepo (backend FastAPI via uv, frontend Next.js/TS/Tailwind),
      env handling, .gitignore hardening, README (Mermaid UML), PLAN/WIP/QUICK-GUIDE.
- [x] **M2 — Backend core**: provider abstractions + registry; Mock, OpenAI, DeepSeek,
      Anthropic, Gemini adapters; `POST /api/chat`; `GET /api/providers`; usage logging on
      every call; pytest suite (Mock only, no network).
- [x] **M3 — Documents + RAG**: upload/extract/list/delete; chunk (~800 tokens, overlap) and
      embed on upload; `POST /api/documents/{id}/summarize` (map-reduce);
      `POST /api/documents/{id}/ask` (cosine top-k retrieval → answer with citations).
- [x] **M4 — Frontend**: app shell + nav (Reader / Chat / Dashboard), dark modern look;
      provider+model picker; Chat page; Reader page (upload dropzone, document list,
      summary card, Q&A with citations).
- [x] **M5 — Dashboard**: Recharts — calls/day, provider distribution, tokens over time;
      filters by date range / provider / model / feature.
- [x] **M6 — Verification + guide**: E2E in browser on Mock; brief live smoke test
      (DeepSeek + OpenAI, cheap models); QUICK-GUIDE verified against reality.

## Later (not v1)

- SSE token streaming in chat and summaries
- Notes, highlights, and bookmarks inside the reader
- Reminders / spaced-repetition prompts from past readings
- Ingest articles by URL, EPUB support
- Real vector store (sqlite-vec or Chroma) behind the existing retrieval interface
- Cost estimation per call (price tables per provider/model)
- Auth / multi-user, deployment beyond localhost

## Key decisions on record

| Decision | Choice | Why |
|---|---|---|
| Q&A grounding | Embeddings RAG from v1 | Better answers on long books; interface hides the store |
| Vector store | numpy over SQLite blobs | Personal scale; zero extra infra; swappable later |
| Providers v1 | Mock, OpenAI, DeepSeek, Anthropic, Gemini | DeepSeek shares OpenAI wire format; Mock enables keyless dev |
| Embeddings | OpenAI `text-embedding-3-small` (Mock offline) | DeepSeek has no embeddings API |
| Streaming | Not in v1 | Simpler adapters + usage logging first |
| DB | SQLite (SQLAlchemy) | Single file, zero setup, fine for one user |
