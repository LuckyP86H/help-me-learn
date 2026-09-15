"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { api, type ProviderInfo } from "./api";

interface LLMContextValue {
  providers: ProviderInfo[];
  provider: string;
  model: string;
  setProvider: (name: string) => void;
  setModel: (model: string) => void;
  loading: boolean;
  error: string | null;
}

const LLMContext = createContext<LLMContextValue | null>(null);

const STORAGE_KEY = "hml-llm-selection";

export function LLMSelectionProvider({ children }: { children: ReactNode }) {
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [provider, setProviderState] = useState("mock");
  const [model, setModel] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getProviders()
      .then((data) => {
        setProviders(data.providers);
        let saved: { provider?: string; model?: string } = {};
        try {
          saved = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "{}");
        } catch {
          // ignore corrupt storage
        }
        const chosen =
          data.providers.find((p) => p.name === saved.provider) ??
          data.providers.find((p) => p.name !== "mock") ??
          data.providers[0];
        if (chosen) {
          setProviderState(chosen.name);
          setModel(
            saved.provider === chosen.name && saved.model && chosen.models.includes(saved.model)
              ? saved.model
              : chosen.default_model,
          );
        }
        setError(null);
      })
      .catch((e: Error) =>
        setError(`Backend unreachable (${e.message}). Is it running on port 8000?`),
      )
      .finally(() => setLoading(false));
  }, []);

  const setProvider = (name: string) => {
    setProviderState(name);
    const info = providers.find((p) => p.name === name);
    if (info) setModel(info.default_model);
  };

  useEffect(() => {
    if (!loading && provider) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ provider, model }));
      } catch {
        // storage unavailable; selection just won't persist
      }
    }
  }, [provider, model, loading]);

  const value = useMemo(
    () => ({ providers, provider, model, setProvider, setModel, loading, error }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [providers, provider, model, loading, error],
  );

  return <LLMContext.Provider value={value}>{children}</LLMContext.Provider>;
}

export function useLLM(): LLMContextValue {
  const ctx = useContext(LLMContext);
  if (!ctx) throw new Error("useLLM must be used inside LLMSelectionProvider");
  return ctx;
}
