# WIP — live progress / recovery file

> Purpose: if a session drops, this file is enough to resume. It's updated at every milestone.
> The roadmap and reasons live in [PLAN.md](PLAN.md); this file is only "where are we right now".

**Last updated**: 2026-09-25 (night) · **Status**: v2 plan revised with the user's answers.
Nothing built yet, by request. Resume tomorrow with the open questions in PLAN.md, then Phase 0.

## State of the world

- v1 merged to `main` (PR #1). The plan work is on branch `docs/v2-plan` (pushed).
- 2026-09-25: audited v1 and wrote the v2 plan (flaws F1–F15, infrastructure I1–I14, Phases 0–5).
- Same night: revised the plan after the user's answers:
  - Reads on Kindle + Apple Books (iPad), so the app is a **companion** built on "bookends"
    (iOS Shortcuts on open/close of the reading app). The in-app reader is parked.
  - **Local-first models** via Ollama, with frontier models as an option.
  - **Gentle weekly goal**, calibrated on two weeks of baseline. The user dogfoods as user #1.
  - Books: AI Engineering, Microservices Patterns, Observability Engineering 2e, SRE, DDIA.
    These led to grounding tiers and a learn-by-building map.

### Evidence gathered (so nobody re-derives it)

- Summary coverage: the real chunker + batching, run on a synthetic 400-page book, stops at
  page 33–50 (8–12%).
- `usage_log.ts` is stored as UTC with no offset; `func.date()` buckets by UTC day.
- README on GitHub: the sequence diagram is fine, but the component diagram is only legible
  in GitHub's expand view.
- Phone width (375 px): the header clips the provider menu and hides the model menu.
  iPad width (768 px) is fine.
- Machine: Apple M3, 24 GB. Ollama 0.34.4 is installed and running. Pulled: llama3.2,
  qwen2.5-coder 1.5b/7b, deepseek-r1:8b, minimax-m2:cloud. No embedding model yet.
  Tailscale is not installed.
- llama3.2 through Ollama's OpenAI-compatible `/v1/chat/completions` took 4.7 s (cold) and
  returned `usage` token counts. Its answer on "error budget" was plausible but imprecise,
  which is the motivation for grounding labels and the eval set.
- Both Mermaid diagrams in PLAN.md were parsed and rendered with Mermaid 11 before committing.
- `npm run lint` is clean; backend tests pass 11/11.

## Next action

1. Get answers to PLAN.md → "Open questions" (book formats, Apple Books sync, Tailscale,
   goal unit). None of them block Phase 0 or Phase 1.
2. `git switch main && git pull`, then `git switch -c v2-phase-0-fixes`.
3. Implement Phase 0. Add tests for local-day bucketing, zero-fill, document counts, and
   query-embedding logging. Do a browser pass at desktop, iPad and iPhone widths, then open a PR.

## How to resume

```bash
# backend (port 8000 is taken by OrbStack on this machine, hence 8801)
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8801
# frontend (separate terminal; port 3000 is also taken, so Next picks the next free port)
cd frontend && npm install && npm run dev
# backend tests
cd backend && uv run pytest
# local models (Ollama runs as a macOS app)
ollama list
```

`.claude/launch.json` holds the same two servers: backend on 8801, frontend on 3100.

## Notes / gotchas for the next session

- Provider adapters live in `backend/app/providers/`. The registry exposes only providers
  whose key is set (Mock is always there). DeepSeek, and soon Ollama, reuse the OpenAI client
  with a different `base_url`.
- Every LLM call must go through `services/usage.py`, because that log feeds the dashboard.
  Known gap until Phase 0: query embeddings in `indexing.embed_query` aren't logged (F3).
- **Tests currently load the real keys from `backend/.env`** (fixed in Phase 0 by I8).
  Until then, never write a test that selects a non-mock provider.
- Adding a column to an existing table needs migrations (I1). `create_all` won't alter the
  existing `backend/data/app.db`.
- Book files stay out of git. The repo is public; `backend/data/` is gitignored. Only use
  copies the user owns, or freely published books.
- The user was advised to rotate the API keys that were shared in chat.
