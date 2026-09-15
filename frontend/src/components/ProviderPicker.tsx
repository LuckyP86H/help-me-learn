"use client";

import { useLLM } from "@/lib/llm-context";

export function ProviderPicker() {
  const { providers, provider, model, setProvider, setModel, loading, error } = useLLM();

  if (loading) {
    return <span className="text-sm text-muted">Loading providers…</span>;
  }
  if (error) {
    return (
      <span className="max-w-72 truncate text-sm text-red-400" title={error}>
        ⚠ {error}
      </span>
    );
  }

  const current = providers.find((p) => p.name === provider);

  return (
    <div className="flex items-center gap-2">
      <span
        className="h-2 w-2 rounded-full bg-[var(--good)] shadow-[0_0_8px_var(--good)]"
        title="Backend connected"
      />
      <select
        aria-label="LLM provider"
        className="input-base"
        value={provider}
        onChange={(e) => setProvider(e.target.value)}
      >
        {providers.map((p) => (
          <option key={p.name} value={p.name}>
            {p.label}
          </option>
        ))}
      </select>
      <select
        aria-label="Model"
        className="input-base"
        value={model}
        onChange={(e) => setModel(e.target.value)}
      >
        {(current?.models ?? []).map((m) => (
          <option key={m} value={m}>
            {m}
          </option>
        ))}
      </select>
    </div>
  );
}
