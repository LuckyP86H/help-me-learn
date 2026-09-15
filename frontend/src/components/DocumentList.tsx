"use client";

import { api, type DocumentInfo } from "@/lib/api";

export function DocumentList({
  documents,
  selectedId,
  onSelect,
  onDeleted,
}: {
  documents: DocumentInfo[];
  selectedId: number | null;
  onSelect: (doc: DocumentInfo) => void;
  onDeleted: (id: number) => void;
}) {
  if (documents.length === 0) {
    return (
      <p className="px-1 text-sm text-muted">
        No documents yet — upload one to start reading faster.
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {documents.map((doc) => {
        const active = doc.id === selectedId;
        return (
          <li key={doc.id}>
            <div
              className={`card group flex cursor-pointer items-center gap-3 p-3 transition-colors ${
                active ? "border-accent shadow-[0_0_12px_var(--accent-glow)]" : "hover:border-accent"
              }`}
              onClick={() => onSelect(doc)}
            >
              <span className="text-xl">{doc.filename.endsWith(".pdf") ? "📕" : "📝"}</span>
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm font-medium">{doc.title}</div>
                <div className="text-xs text-muted">
                  {doc.num_pages} page{doc.num_pages === 1 ? "" : "s"} ·{" "}
                  {(doc.num_chars / 1000).toFixed(0)}k chars
                  {doc.num_chunks != null && ` · ${doc.num_chunks} chunks`}
                </div>
              </div>
              <button
                type="button"
                aria-label={`Delete ${doc.title}`}
                className="rounded p-1 text-muted opacity-0 transition-opacity hover:text-red-400 group-hover:opacity-100"
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm(`Delete "${doc.title}" and its index?`)) {
                    void api.deleteDocument(doc.id).then(() => onDeleted(doc.id));
                  }
                }}
              >
                ✕
              </button>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
