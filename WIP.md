# WIP — live progress / recovery file

> Purpose: if a session drops, this file is enough to resume. Updated at every milestone.
> Roadmap lives in [PLAN.md](PLAN.md); this file is only "where are we right now".

**Last updated**: 2026-09-15 · **Status**: v1 complete (M1–M6 all done, E2E verified)

## State of the world

- [x] M1 scaffold done: `backend/` (FastAPI, uv-managed, deps installed via `uv sync`),
      `frontend/` (create-next-app: TS, Tailwind, App Router, src dir, npm).
- [x] `.env.example` (placeholders) at repo root; real keys in `backend/.env` (gitignored — verified
      with `git check-ignore`). Keys present: OpenAI, DeepSeek, Anthropic, Gemini.
      Live testing budget: DeepSeek + OpenAI only (others may lack credit).
- [x] `.gitignore` extended: `backend/data/`, Next.js artifacts, and a `!frontend/src/lib/`
      negation (the Python template's bare `lib/` pattern would have ignored it).
- [x] README.md (Mermaid diagrams), PLAN.md, QUICK-GUIDE.md written.
- [x] M2 backend core: provider ABCs (`app/providers/base.py`), adapters (mock, OpenAI,
      DeepSeek, Anthropic, Gemini), registry, `/api/chat`, `/api/providers`, usage logging
      (`services/usage.py`), `/api/usage` aggregates.
- [x] M3 documents + RAG: upload/extract (`services/documents.py`), chunk+embed
      (`indexing.py`), cosine top-k (`retrieval.py`), map-reduce summarize, Q&A with
      citations. **All 11 pytest tests pass** (`uv run pytest`, mock only, no network).
- [x] M4 frontend: dark app shell + nav, provider/model picker (persists in localStorage),
      Reader (upload dropzone, doc list, summary, Q&A with citations), Chat page.
      `npm run build` passes clean.
- [x] M5 dashboard: stat tiles, calls/day bar, provider donut, tokens/day area, by-model
      table; filters for date range / provider / model / feature. Chart animations disabled
      (`isAnimationActive={false}`) — snappier and screenshot-safe.
- [x] M6 verified E2E in the browser: mock chat, upload → summarize → ask (citations
      shown), dashboard reflects all calls including embeddings. Live smoke test passed:
      DeepSeek chat + OpenAI RAG answer + OpenAI embeddings, all logged correctly.

## Next ideas (v2 candidates, see PLAN.md "Later")

- SSE streaming; notes/highlights; URL ingestion; cost-per-call estimates.

## How to resume

```bash
# backend
# NOTE: port 8000 is occupied by OrbStack on this machine, hence 8801
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8801
# frontend (separate terminal)
cd frontend && npm install && npm run dev   # http://localhost:3000
# backend tests
cd backend && uv run pytest
```

## Notes / gotchas for the next session

- Provider adapters live in `backend/app/providers/`; registry exposes only providers whose
  key is set (Mock always). DeepSeek reuses the OpenAI client with `base_url=https://api.deepseek.com`.
- Every LLM call must be logged through `services/usage.py` — that feeds the dashboard.
- Embeddings default to OpenAI; `EMBEDDING_PROVIDER=mock` in `backend/.env` for offline work.
- Automated tests must never hit the network (Mock provider/embedder only).
- User has been advised to rotate the API keys after setup (they were shared in chat).
