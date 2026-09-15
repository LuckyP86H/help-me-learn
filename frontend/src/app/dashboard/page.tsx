"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { api, type UsageStats } from "@/lib/api";
import { useLLM } from "@/lib/llm-context";
import {
  DailyCallsChart,
  ModelTable,
  ProviderDonut,
  TokensChart,
  formatTokens,
} from "@/components/UsageCharts";

const RANGES = [
  { label: "All time", days: null },
  { label: "Last 7 days", days: 7 },
  { label: "Last 30 days", days: 30 },
  { label: "Last 90 days", days: 90 },
] as const;

const FEATURES = ["chat", "summarize", "qa", "embed"] as const;

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="card p-4">
      <div className="text-xs uppercase tracking-wide text-muted">{label}</div>
      <div className="mt-1 text-2xl font-semibold">{value}</div>
    </div>
  );
}

export default function DashboardPage() {
  const { providers } = useLLM();
  const [rangeDays, setRangeDays] = useState<number | null>(30);
  const [provider, setProvider] = useState("");
  const [feature, setFeature] = useState("");
  const [model, setModel] = useState("");
  const [stats, setStats] = useState<UsageStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  const start = useMemo(() => {
    if (rangeDays === null) return undefined;
    const d = new Date();
    d.setDate(d.getDate() - rangeDays);
    return d.toISOString().slice(0, 10);
  }, [rangeDays]);

  const load = useCallback(() => {
    api
      .getUsage({
        start,
        provider: provider || undefined,
        feature: feature || undefined,
        model: model || undefined,
      })
      .then((data) => {
        setStats(data);
        setError(null);
      })
      .catch((e: Error) => setError(e.message));
  }, [start, provider, feature, model]);

  useEffect(() => {
    load();
  }, [load]);

  // Model options come from what actually appears in the (unfiltered-by-model) data.
  const [modelOptions, setModelOptions] = useState<string[]>([]);
  useEffect(() => {
    api
      .getUsage({ start, provider: provider || undefined, feature: feature || undefined })
      .then((data) => setModelOptions(data.by_model.map((r) => r.model)))
      .catch(() => setModelOptions([]));
  }, [start, provider, feature]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-2">
        <h1 className="mr-auto text-lg font-semibold">Usage dashboard</h1>
        <select
          aria-label="Date range"
          className="input-base"
          value={rangeDays ?? "all"}
          onChange={(e) =>
            setRangeDays(e.target.value === "all" ? null : Number(e.target.value))
          }
        >
          {RANGES.map((r) => (
            <option key={r.label} value={r.days ?? "all"}>
              {r.label}
            </option>
          ))}
        </select>
        <select
          aria-label="Provider filter"
          className="input-base"
          value={provider}
          onChange={(e) => {
            setProvider(e.target.value);
            setModel("");
          }}
        >
          <option value="">All providers</option>
          {providers.map((p) => (
            <option key={p.name} value={p.name}>
              {p.label}
            </option>
          ))}
        </select>
        <select
          aria-label="Model filter"
          className="input-base"
          value={model}
          onChange={(e) => setModel(e.target.value)}
        >
          <option value="">All models</option>
          {modelOptions.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
        <select
          aria-label="Feature filter"
          className="input-base"
          value={feature}
          onChange={(e) => setFeature(e.target.value)}
        >
          <option value="">All features</option>
          {FEATURES.map((f) => (
            <option key={f} value={f}>
              {f}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <p className="text-sm text-red-400">⚠ Could not load usage: {error}</p>
      )}

      {stats && (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <StatTile label="LLM calls" value={String(stats.totals.calls)} />
            <StatTile label="Input tokens" value={formatTokens(stats.totals.input_tokens)} />
            <StatTile label="Output tokens" value={formatTokens(stats.totals.output_tokens)} />
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <DailyCallsChart stats={stats} />
            <ProviderDonut stats={stats} />
            <TokensChart stats={stats} />
            <ModelTable stats={stats} />
          </div>
        </>
      )}
    </div>
  );
}
