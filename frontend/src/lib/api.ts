const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8801";

export interface ProviderInfo {
  name: string;
  label: string;
  models: string[];
  default_model: string;
}

export interface ProvidersResponse {
  providers: ProviderInfo[];
  embedding_provider: string;
}

export interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  text: string;
  provider: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  latency_ms: number;
}

export interface DocumentInfo {
  id: number;
  filename: string;
  title: string;
  created_at: string;
  num_pages: number;
  num_chars: number;
  embedder: string;
  num_chunks?: number;
}

export interface SummaryResponse {
  summary: string;
  truncated: boolean;
  llm_calls: number;
  provider: string;
  model: string;
}

export interface Citation {
  n: number;
  page: number;
  score: number;
  snippet: string;
}

export interface AskResponse {
  answer: string;
  citations: Citation[];
  provider: string;
  model: string;
  latency_ms: number;
}

export interface UsageStats {
  daily: { date: string; calls: number; input_tokens: number; output_tokens: number }[];
  by_provider: {
    provider: string;
    calls: number;
    input_tokens: number;
    output_tokens: number;
    avg_latency_ms: number;
  }[];
  by_model: {
    provider: string;
    model: string;
    calls: number;
    input_tokens: number;
    output_tokens: number;
  }[];
  by_feature: { feature: string; calls: number; input_tokens: number; output_tokens: number }[];
  totals: { calls: number; input_tokens: number; output_tokens: number };
}

export interface UsageFilters {
  start?: string;
  end?: string;
  provider?: string;
  model?: string;
  feature?: string;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, init);
  if (!resp.ok) {
    let detail = resp.statusText;
    try {
      const body = await resp.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // non-JSON error body; keep statusText
    }
    throw new Error(detail);
  }
  return resp.json();
}

function post<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export const api = {
  getProviders: () => request<ProvidersResponse>("/api/providers"),

  chat: (provider: string, model: string | null, messages: ChatMessage[]) =>
    post<ChatResponse>("/api/chat", { provider, model, messages }),

  listDocuments: () => request<DocumentInfo[]>("/api/documents"),

  uploadDocument: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<DocumentInfo>("/api/documents", { method: "POST", body: form });
  },

  deleteDocument: (id: number) =>
    request<{ deleted: number }>(`/api/documents/${id}`, { method: "DELETE" }),

  summarize: (id: number, provider: string, model: string | null) =>
    post<SummaryResponse>(`/api/documents/${id}/summarize`, { provider, model }),

  ask: (id: number, provider: string, model: string | null, question: string) =>
    post<AskResponse>(`/api/documents/${id}/ask`, { provider, model, question }),

  getUsage: (filters: UsageFilters) => {
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(filters)) {
      if (value) params.set(key, value);
    }
    const query = params.toString();
    return request<UsageStats>(`/api/usage${query ? `?${query}` : ""}`);
  },
};
