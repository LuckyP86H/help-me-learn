"use client";

import { useRef, useState } from "react";
import { api, type DocumentInfo } from "@/lib/api";

export function UploadDropzone({ onUploaded }: { onUploaded: (doc: DocumentInfo) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upload = async (file: File) => {
    setBusy(true);
    setError(null);
    try {
      onUploaded(await api.uploadDocument(file));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <button
        type="button"
        className={`card w-full cursor-pointer border-dashed p-6 text-center transition-colors ${
          dragging ? "border-accent bg-surface-2" : "hover:border-accent"
        }`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          const file = e.dataTransfer.files[0];
          if (file) void upload(file);
        }}
        disabled={busy}
      >
        {busy ? (
          <span className="text-sm text-muted">
            Extracting & indexing
            <span className="thinking-dot"> ●</span>
            <span className="thinking-dot">●</span>
            <span className="thinking-dot">●</span>
          </span>
        ) : (
          <>
            <div className="text-2xl">📄</div>
            <div className="mt-1 text-sm font-medium">Drop a PDF here, or click to browse</div>
            <div className="mt-0.5 text-xs text-muted">.pdf · .txt · .md — up to 50 MB</div>
          </>
        )}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.txt,.md"
        hidden
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) void upload(file);
          e.target.value = "";
        }}
      />
      {error && <p className="mt-2 text-sm text-red-400">⚠ {error}</p>}
    </div>
  );
}
