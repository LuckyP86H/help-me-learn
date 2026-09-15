# QUICK-GUIDE — help-me-learn

Get the app running and learn the three screens in ~5 minutes.

## 1. Prerequisites

- Python 3.11+ and [uv](https://docs.astral.sh/uv/) (`brew install uv`)
- Node.js 20+ and npm

## 2. Configure API keys

```bash
cp .env.example backend/.env
```

Edit `backend/.env` and paste the keys you have. **Any subset works** — a provider only
shows up in the app when its key is set, and the built-in **mock** provider always works
with no keys at all (canned responses, great for trying the UI).

| Variable | Provider | Notes |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI | Also powers document embeddings (RAG) |
| `DEEPSEEK_API_KEY` | DeepSeek | |
| `ANTHROPIC_API_KEY` | Anthropic (Claude) | |
| `GEMINI_API_KEY` | Google Gemini | |
| `EMBEDDING_PROVIDER` | `openai` or `mock` | Use `mock` to index documents offline |

`backend/.env` is gitignored — keys never leave your machine.

## 3. Run it

Backend (terminal 1):

```bash
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8801
```

Frontend (terminal 2):

```bash
cd frontend && npm install && npm run dev
```

Open **http://localhost:3000** (if 3000 is busy — e.g. OrbStack holds it — Next picks the
next free port and prints it; the backend accepts any localhost port).

## 4. The three screens

### Reader (home) — the core feature
1. Drag a PDF (or .txt/.md) onto the upload zone. It's extracted, chunked, and indexed.
2. Pick a provider + model in the top bar — this is the "brain" used for the next step.
3. Click **Summarize** for a condensed overview of the whole document.
4. Ask questions in the Q&A panel — answers are grounded in the document and cite the
   passages they came from.

### Chat
Plain conversation with whichever provider/model you select. Handy for comparing how
different models answer the same question.

### Dashboard
Every LLM call (chat, summarize, Q&A) is logged locally. Charts show calls per day,
provider share, and token consumption over time — filter by date range, provider, model,
or feature to see your patterns.

## 5. Switching providers

Just change the dropdown — no restart needed. To add a key later, put it in
`backend/.env` and restart the backend; the provider appears automatically.

## Troubleshooting

- **Provider missing from dropdown** → its key isn't set in `backend/.env`, or the backend
  wasn't restarted after adding it.
- **Upload works but Q&A fails** → embeddings need `OPENAI_API_KEY`, or set
  `EMBEDDING_PROVIDER=mock` (offline, lower answer quality).
- **CORS / network errors in the UI** → make sure the backend is on port 8801
  (the frontend calls `http://localhost:8801/api/...`; override with
  `NEXT_PUBLIC_API_BASE` in `frontend/.env.local` if you run it elsewhere).
- **Reset all data** → stop the backend and delete `backend/data/` (DB + uploads).
