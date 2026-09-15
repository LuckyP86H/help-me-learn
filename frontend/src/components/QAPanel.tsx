"use client";

import { useState } from "react";
import { api, type AskResponse, type DocumentInfo } from "@/lib/api";
import { useLLM } from "@/lib/llm-context";

interface QAEntry {
  question: string;
  response: AskResponse;
}

export function QAPanel({ document }: { document: DocumentInfo }) {
  const { provider, model } = useLLM();
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<QAEntry[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openCitations, setOpenCitations] = useState<number | null>(null);

  const ask = async () => {
    const q = question.trim();
    if (!q || busy) return;
    setBusy(true);
    setError(null);
    try {
      const response = await api.ask(document.id, provider, model || null, q);
      setHistory((h) => [...h, { question: q, response }]);
      setQuestion("");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="card p-4">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">
        Ask this document
      </h2>

      <div className="mt-3 space-y-4">
        {history.map((entry, i) => (
          <div key={i} className="rise-in">
            <p className="text-sm font-medium text-accent-soft">You: {entry.question}</p>
            <p className="mt-1 whitespace-pre-wrap text-sm leading-relaxed">
              {entry.response.answer}
            </p>
            <button
              type="button"
              className="mt-1.5 text-xs text-muted underline-offset-2 hover:text-foreground hover:underline"
              onClick={() => setOpenCitations(openCitations === i ? null : i)}
            >
              {openCitations === i ? "Hide" : "Show"} {entry.response.citations.length}{" "}
              cited passage{entry.response.citations.length === 1 ? "" : "s"} ·{" "}
              {entry.response.provider}/{entry.response.model}
            </button>
            {openCitations === i && (
              <ul className="mt-2 space-y-2">
                {entry.response.citations.map((c) => (
                  <li
                    key={c.n}
                    className="rounded-lg border border-borderc bg-surface-2 p-2.5 text-xs leading-relaxed text-muted"
                  >
                    <span className="font-semibold text-accent-soft">
                      [{c.n}] page {c.page}
                    </span>{" "}
                    — {c.snippet}…
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
        {busy && (
          <p className="text-sm text-muted">
            Reading the relevant passages
            <span className="thinking-dot"> ●</span>
            <span className="thinking-dot">●</span>
            <span className="thinking-dot">●</span>
          </p>
        )}
        {error && <p className="text-sm text-red-400">⚠ {error}</p>}
      </div>

      <form
        className="mt-4 flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          void ask();
        }}
      >
        <input
          className="input-base flex-1"
          placeholder={`e.g. “What is the main argument of ${document.title}?”`}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={busy}
        />
        <button type="submit" className="btn-primary" disabled={busy || !question.trim()}>
          Ask
        </button>
      </form>
    </section>
  );
}
