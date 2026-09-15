"use client";

import { useState } from "react";
import { api, type DocumentInfo, type SummaryResponse } from "@/lib/api";
import { useLLM } from "@/lib/llm-context";

export function SummaryCard({ document }: { document: DocumentInfo }) {
  const { provider, model } = useLLM();
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    setBusy(true);
    setError(null);
    try {
      setSummary(await api.summarize(document.id, provider, model || null));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="card p-4">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">
          Summary
        </h2>
        <button type="button" className="btn-primary" onClick={run} disabled={busy}>
          {busy ? "Summarizing…" : summary ? "Re-summarize" : "⚡ Summarize"}
        </button>
      </div>
      {error && <p className="mt-3 text-sm text-red-400">⚠ {error}</p>}
      {summary && (
        <div className="rise-in mt-3">
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{summary.summary}</p>
          <p className="mt-3 text-xs text-muted">
            {summary.provider} · {summary.model} · {summary.llm_calls} call
            {summary.llm_calls === 1 ? "" : "s"}
            {summary.truncated && " · ⚠ document was truncated for length"}
          </p>
        </div>
      )}
      {!summary && !busy && !error && (
        <p className="mt-3 text-sm text-muted">
          Condense “{document.title}” into its key ideas with the selected model.
        </p>
      )}
    </section>
  );
}
