"use client";

import { useEffect, useState } from "react";
import { api, type DocumentInfo } from "@/lib/api";
import { DocumentList } from "@/components/DocumentList";
import { QAPanel } from "@/components/QAPanel";
import { SummaryCard } from "@/components/SummaryCard";
import { UploadDropzone } from "@/components/UploadDropzone";

export default function ReaderPage() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [selected, setSelected] = useState<DocumentInfo | null>(null);

  useEffect(() => {
    api
      .listDocuments()
      .then((docs) => {
        setDocuments(docs);
        setSelected((current) => current ?? docs[0] ?? null);
      })
      .catch(() => {
        // Backend down: the nav's provider picker already surfaces this.
      });
  }, []);

  return (
    <div className="grid gap-6 md:grid-cols-[minmax(16rem,1fr)_2fr]">
      <aside className="space-y-4">
        <UploadDropzone
          onUploaded={(doc) => {
            setDocuments((docs) => [doc, ...docs]);
            setSelected(doc);
          }}
        />
        <DocumentList
          documents={documents}
          selectedId={selected?.id ?? null}
          onSelect={setSelected}
          onDeleted={(id) => {
            setDocuments((docs) => docs.filter((d) => d.id !== id));
            setSelected((cur) => (cur?.id === id ? null : cur));
          }}
        />
      </aside>

      <div className="space-y-4">
        {selected ? (
          <>
            <div className="px-1">
              <h1 className="text-lg font-semibold">{selected.title}</h1>
              <p className="text-xs text-muted">
                {selected.filename} · indexed with the “{selected.embedder}” embedder
              </p>
            </div>
            <SummaryCard key={`sum-${selected.id}`} document={selected} />
            <QAPanel key={`qa-${selected.id}`} document={selected} />
          </>
        ) : (
          <div className="card grid min-h-64 place-items-center p-8 text-center">
            <div>
              <div className="text-3xl">🧠</div>
              <h1 className="mt-2 font-semibold">Learn faster from anything you read</h1>
              <p className="mx-auto mt-1 max-w-sm text-sm text-muted">
                Upload a book chapter, paper, or article. Get a summary, then ask
                questions — answers cite the exact passages they came from.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
