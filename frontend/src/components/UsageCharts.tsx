"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { UsageStats } from "@/lib/api";

// Categorical colors follow the provider (entity), never its rank.
// Validated for CVD safety on the card surface with the dataviz palette checker.
const PROVIDER_COLORS: Record<string, string> = {
  openai: "#3987e5",
  deepseek: "#d95926",
  anthropic: "#199e70",
  gemini: "#c98500",
  mock: "#d55181",
};
const FALLBACK_COLOR = "#9085e9";

export const providerColor = (name: string) => PROVIDER_COLORS[name] ?? FALLBACK_COLOR;

const INK_MUTED = "#8b91a7";
const GRID = "#262b3d";
const SURFACE = "#12151f";
const SERIES_BLUE = "#3987e5";
const SERIES_BLUE_LIGHT = "#86b6ef";

const tooltipStyle = {
  backgroundColor: "#191d2b",
  border: `1px solid ${GRID}`,
  borderRadius: 8,
  fontSize: 12,
  color: "#e7e9f0",
};

export function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return String(n);
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="card p-4">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted">
        {title}
      </h2>
      {children}
    </section>
  );
}

export function DailyCallsChart({ stats }: { stats: UsageStats }) {
  return (
    <ChartCard title="Calls per day">
      {stats.daily.length === 0 ? (
        <p className="text-sm text-muted">No calls in this range.</p>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={stats.daily} barCategoryGap="35%">
            <CartesianGrid stroke={GRID} strokeDasharray="0" vertical={false} />
            <XAxis
              dataKey="date"
              tick={{ fill: INK_MUTED, fontSize: 11 }}
              axisLine={{ stroke: GRID }}
              tickLine={false}
            />
            <YAxis
              allowDecimals={false}
              tick={{ fill: INK_MUTED, fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={32}
            />
            <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(124,108,246,0.08)" }} />
            <Bar isAnimationActive={false} dataKey="calls" fill={SERIES_BLUE} radius={[4, 4, 0, 0]} maxBarSize={36} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  );
}

export function ProviderDonut({ stats }: { stats: UsageStats }) {
  const data = stats.by_provider.map((row) => ({ name: row.provider, value: row.calls }));
  return (
    <ChartCard title="Calls by provider">
      {data.length === 0 ? (
        <p className="text-sm text-muted">No calls in this range.</p>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              isAnimationActive={false}
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius="55%"
              outerRadius="85%"
              paddingAngle={2}
              stroke={SURFACE}
              strokeWidth={2}
              label={({ name, percent }) =>
                `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
              }
              labelLine={false}
              fontSize={11}
            >
              {data.map((entry) => (
                <Cell key={entry.name} fill={providerColor(entry.name)} />
              ))}
            </Pie>
            <Tooltip contentStyle={tooltipStyle} />
            <Legend
              formatter={(value: string) => (
                <span style={{ color: INK_MUTED, fontSize: 12 }}>{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  );
}

export function TokensChart({ stats }: { stats: UsageStats }) {
  return (
    <ChartCard title="Tokens per day">
      {stats.daily.length === 0 ? (
        <p className="text-sm text-muted">No calls in this range.</p>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={stats.daily}>
            <CartesianGrid stroke={GRID} vertical={false} />
            <XAxis
              dataKey="date"
              tick={{ fill: INK_MUTED, fontSize: 11 }}
              axisLine={{ stroke: GRID }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: INK_MUTED, fontSize: 11 }}
              tickFormatter={formatTokens}
              axisLine={false}
              tickLine={false}
              width={44}
            />
            <Tooltip
              contentStyle={tooltipStyle}
              formatter={(value) => formatTokens(Number(value))}
            />
            <Legend
              formatter={(value: string) => (
                <span style={{ color: INK_MUTED, fontSize: 12 }}>{value}</span>
              )}
            />
            <Area
              isAnimationActive={false}
              type="monotone"
              dataKey="input_tokens"
              name="input tokens"
              stackId="tok"
              stroke={SERIES_BLUE_LIGHT}
              fill={SERIES_BLUE_LIGHT}
              fillOpacity={0.35}
              strokeWidth={2}
            />
            <Area
              isAnimationActive={false}
              type="monotone"
              dataKey="output_tokens"
              name="output tokens"
              stackId="tok"
              stroke={SERIES_BLUE}
              fill={SERIES_BLUE}
              fillOpacity={0.35}
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  );
}

export function ModelTable({ stats }: { stats: UsageStats }) {
  return (
    <ChartCard title="By model">
      {stats.by_model.length === 0 ? (
        <p className="text-sm text-muted">No calls in this range.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-borderc text-left text-xs uppercase tracking-wide text-muted">
                <th className="pb-2 pr-3 font-medium">Provider</th>
                <th className="pb-2 pr-3 font-medium">Model</th>
                <th className="pb-2 pr-3 text-right font-medium">Calls</th>
                <th className="pb-2 pr-3 text-right font-medium">Input tok</th>
                <th className="pb-2 text-right font-medium">Output tok</th>
              </tr>
            </thead>
            <tbody className="[font-variant-numeric:tabular-nums]">
              {stats.by_model.map((row) => (
                <tr key={`${row.provider}/${row.model}`} className="border-b border-borderc/50">
                  <td className="py-2 pr-3">
                    <span
                      className="mr-2 inline-block h-2.5 w-2.5 rounded-sm align-middle"
                      style={{ backgroundColor: providerColor(row.provider) }}
                    />
                    {row.provider}
                  </td>
                  <td className="py-2 pr-3 text-muted">{row.model}</td>
                  <td className="py-2 pr-3 text-right">{row.calls}</td>
                  <td className="py-2 pr-3 text-right">{formatTokens(row.input_tokens)}</td>
                  <td className="py-2 text-right">{formatTokens(row.output_tokens)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </ChartCard>
  );
}
