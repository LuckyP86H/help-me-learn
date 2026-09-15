# help-me-learn

A personal, **LLM-agnostic learning agent**: upload a book or article (PDF/text), get fast
summaries, ask questions grounded in the document (RAG with citations), and watch your own
usage patterns on a dashboard — while switching freely between OpenAI, DeepSeek, Anthropic,
Gemini, or an offline mock provider.

- **Frontend**: Next.js + TypeScript + Tailwind (Reader, Chat, Dashboard)
- **Backend**: Python + FastAPI (provider adapters, RAG pipeline, SQLite usage log)
- **Setup & usage**: see [QUICK-GUIDE.md](QUICK-GUIDE.md) · **Roadmap**: [PLAN.md](PLAN.md) · **Current status**: [WIP.md](WIP.md)

## How the pieces fit

```mermaid
flowchart LR
    subgraph Frontend["Frontend — Next.js / TypeScript"]
        Reader["Reader page\n(upload · summarize · ask)"]
        Chat["Chat page"]
        Dash["Dashboard\n(usage charts + filters)"]
        API["api.ts\ntyped API client"]
        Reader --> API
        Chat --> API
        Dash --> API
    end

    subgraph Backend["Backend — FastAPI / Python"]
        Routers["Routers\n/chat /documents /usage /providers"]
        Docs["Document service\npypdf extract · chunk"]
        Index["Indexing + Retrieval\nembed chunks · cosine top-k"]
        Sum["Summarize\n(map-reduce)"]
        QA["Q&A\n(RAG + citations)"]
        Usage["Usage service\nlog every LLM call"]
        Registry["Provider registry"]
        Routers --> Docs
        Routers --> Sum
        Routers --> QA
        Routers --> Usage
        Docs --> Index
        QA --> Index
        Sum --> Registry
        QA --> Registry
        Routers --> Registry
        Registry --> Usage
    end

    subgraph Providers["LLM providers (adapters)"]
        Mock["Mock\n(no key needed)"]
        OpenAI["OpenAI"]
        DeepSeek["DeepSeek"]
        Anthropic["Anthropic"]
        Gemini["Gemini"]
    end

    DB[("SQLite\ndocuments · chunks+vectors · usage")]

    API -- "HTTP/JSON" --> Routers
    Registry --> Mock & OpenAI & DeepSeek & Anthropic & Gemini
    Docs --> DB
    Index --> DB
    Usage --> DB
```

## The core flow: upload a book, ask a question

```mermaid
sequenceDiagram
    actor You
    participant UI as Reader (Next.js)
    participant BE as FastAPI
    participant EMB as Embedding provider
    participant LLM as Chat provider (your pick)
    participant DB as SQLite

    You->>UI: Upload PDF
    UI->>BE: POST /api/documents
    BE->>BE: Extract text (pypdf), chunk
    BE->>EMB: Embed chunks
    BE->>DB: Store text + vectors
    You->>UI: "What's the key argument of chapter 2?"
    UI->>BE: POST /api/documents/{id}/ask
    BE->>EMB: Embed question
    BE->>DB: Cosine top-k chunks
    BE->>LLM: Question + retrieved chunks
    LLM-->>BE: Answer
    BE->>DB: Log usage (provider, model, tokens)
    BE-->>UI: Answer + cited passages
```

Every LLM call — chat, summarize, or Q&A — lands one row in the usage log, which is what the
dashboard aggregates (calls per day, provider share, tokens over time, filterable by date,
provider, model, and feature).
