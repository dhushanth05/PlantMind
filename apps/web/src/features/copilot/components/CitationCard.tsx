import { useState } from "react";
import { ChevronDown, ExternalLink, FileText } from "lucide-react";

import { cn } from "@/lib/utils";

import type { Citation } from "../types";

export function CitationCard({ citation, index }: { citation: Citation; index: number }) {
  const [expanded, setExpanded] = useState(index === 0);
  const pageLabel = citation.page_number ? `Page ${citation.page_number}` : citation.page_reference ?? "Source page";

  return (
    <article className="rounded-md border border-border bg-white dark:bg-slate-950">
      <button
        onClick={() => setExpanded((value) => !value)}
        className="flex w-full items-center justify-between gap-3 px-3 py-3 text-left"
      >
        <span className="flex min-w-0 items-center gap-2">
          <FileText className="h-4 w-4 shrink-0 text-primary" />
          <span className="min-w-0">
            <span className="block truncate text-sm font-semibold">{citation.document ?? citation.document_id}</span>
            <span className="block text-xs text-slate-500 dark:text-slate-400">
              {pageLabel} / {Math.round(citation.confidence * 100)}% confidence
            </span>
          </span>
        </span>
        <ChevronDown className={cn("h-4 w-4 shrink-0 transition", expanded && "rotate-180")} />
      </button>
      {expanded ? (
        <div className="border-t border-border px-3 py-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
          {citation.evidence ?? citation.quote ?? "Citation source is linked but no evidence snippet was returned."}
          <div className="mt-3 flex flex-wrap gap-2">
            <a
              href={`/documents?documentId=${encodeURIComponent(citation.document_id)}${citation.page_number ? `&page=${citation.page_number}` : ""}`}
              className="inline-flex h-8 items-center gap-1 rounded-md border border-border px-2 text-xs font-medium hover:border-primary"
            >
              Open source
              <ExternalLink className="h-3 w-3" />
            </a>
            {citation.chunk_id ? (
              <span className="inline-flex h-8 items-center rounded-md bg-slate-100 px-2 font-mono text-xs text-slate-500 dark:bg-slate-900 dark:text-slate-400">
                {citation.chunk_id}
              </span>
            ) : null}
          </div>
        </div>
      ) : null}
    </article>
  );
}
