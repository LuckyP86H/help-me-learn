"use client";

import { useEffect, useRef, useState } from "react";
import { api, type ChatMessage } from "@/lib/api";
import { useLLM } from "@/lib/llm-context";

interface DisplayMessage extends ChatMessage {
  meta?: string;
}

export default function ChatPage() {
  const { provider, model } = useLLM();
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  const send = async () => {
    const content = input.trim();
    if (!content || busy) return;
    const next: DisplayMessage[] = [...messages, { role: "user", content }];
    setMessages(next);
    setInput("");
    setBusy(true);
    setError(null);
    try {
      const resp = await api.chat(
        provider,
        model || null,
        next.map(({ role, content }) => ({ role, content })),
      );
      setMessages([
        ...next,
        {
          role: "assistant",
          content: resp.text,
          meta: `${resp.provider}/${resp.model} · ${resp.output_tokens} tok · ${(
            resp.latency_ms / 1000
          ).toFixed(1)}s`,
        },
      ]);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto flex h-[calc(100vh-8.5rem)] max-w-3xl flex-col">
      <div className="flex-1 space-y-4 overflow-y-auto pb-4 pr-1">
        {messages.length === 0 && (
          <div className="grid h-full place-items-center text-center">
            <div>
              <div className="text-3xl">💬</div>
              <h1 className="mt-2 font-semibold">Talk to any model</h1>
              <p className="mt-1 max-w-sm text-sm text-muted">
                Same conversation, any provider — switch models in the top bar to
                compare answers. Every call lands on your dashboard.
              </p>
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`rise-in flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-gradient-to-br from-accent to-sky-600 text-white"
                  : "card"
              }`}
            >
              <p className="whitespace-pre-wrap">{m.content}</p>
              {m.meta && <p className="mt-1.5 text-xs opacity-60">{m.meta}</p>}
            </div>
          </div>
        ))}
        {busy && (
          <p className="text-sm text-muted">
            {provider} is thinking
            <span className="thinking-dot"> ●</span>
            <span className="thinking-dot">●</span>
            <span className="thinking-dot">●</span>
          </p>
        )}
        {error && <p className="text-sm text-red-400">⚠ {error}</p>}
        <div ref={bottomRef} />
      </div>

      <form
        className="flex gap-2 border-t border-borderc pt-4"
        onSubmit={(e) => {
          e.preventDefault();
          void send();
        }}
      >
        <input
          className="input-base flex-1"
          placeholder={`Message ${provider}…`}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={busy}
        />
        <button type="submit" className="btn-primary" disabled={busy || !input.trim()}>
          Send ↵
        </button>
        {messages.length > 0 && (
          <button
            type="button"
            className="btn-ghost"
            onClick={() => {
              setMessages([]);
              setError(null);
            }}
          >
            Clear
          </button>
        )}
      </form>
    </div>
  );
}
