# WIP — live progress / recovery file

> Purpose: if a session drops, this file is enough to resume. It's updated at every milestone.
> The roadmap and reasons live in [PLAN.md](PLAN.md); this file is only "where are we right now".

**Last updated**: 2026-09-25 · **Status**: v1 merged. v2 is planned but not started,
waiting on the open decisions in PLAN.md → "Open decisions" (Phase 0 can start regardless).

## State of the world

- v1 merged to `main` (PR #1, 2026-09-15). The local checkout is on an up-to-date `main`.
- 2026-09-25: audited v1 and wrote the v2 plan into PLAN.md (flaws F1–F14,
  infrastructure I1–I11, Phases 0–5). **No code changed yet.**
- Evidence behind the audit, so nobody has to re-derive it:
  - Summary coverage: ran the real chunker + batching on a synthetic 400-page book.
    The summary stops at page 33 (3,000 chars/page) or page 50 (2,000 chars/page).
  - `usage_log.ts` is stored as UTC with no offset, and `func.date()` buckets by UTC day.
  - README on GitHub: the sequence diagram is fine, but the component diagram is only legible
    in GitHub's expand view.
  - `npm run lint` is clean; backend tests pass 11/11.

## Next action

1. `git switch -c v2-phase-0-fixes` from `main`.
2. Implement Phase 0 (PLAN.md → Phases). Add tests for local-day bucketing, zero-fill,
   document counts, and query-embedding logging.
3. Browser pass on Reader, Chat, and Dashboard, including the backend-down state. Then open a PR.

## How to resume

```bash
# backend (port 8000 is taken by OrbStack on this machine, hence 8801)
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8801
# frontend (separate terminal; port 3000 is also taken, so Next picks the next free port)
cd frontend && npm install && npm run dev
# backend tests
cd backend && uv run pytest
```

`.claude/launch.json` holds the same two servers: backend on 8801, frontend on 3100.

## Notes / gotchas for the next session

- Provider adapters live in `backend/app/providers/`. The registry exposes only providers
  whose key is set (Mock is always there). DeepSeek reuses the OpenAI client with
  `base_url=https://api.deepseek.com`.
- Every LLM call must go through `services/usage.py`, because that log feeds the dashboard.
  Known gap until Phase 0: query embeddings in `indexing.embed_query` aren't logged (F3).
- Embeddings default to OpenAI. Set `EMBEDDING_PROVIDER=mock` in `backend/.env` for offline work.
- **Tests currently load the real keys from `backend/.env`** (fixed in Phase 0 by I8).
  Until then, never write a test that selects a non-mock provider.
- Adding a column to an existing table needs migrations (I1). `create_all` won't alter the
  user's existing `backend/data/app.db`.
- The user was advised to rotate the API keys that were shared in chat.
