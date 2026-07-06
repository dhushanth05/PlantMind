import { FormEvent, useState } from "react";
import { Search } from "lucide-react";

import type { ApiGraphNode } from "../types";

type GraphSearchBarProps = {
  onSearch: (query: string) => void;
  results: ApiGraphNode[];
  onSelect: (node: ApiGraphNode) => void;
};

export function GraphSearchBar({ onSearch, results, onSelect }: GraphSearchBarProps) {
  const [query, setQuery] = useState("");

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (query.trim()) onSearch(query.trim());
  };

  return (
    <div className="absolute left-4 top-16 z-10 w-[min(420px,calc(100%-2rem))]">
      <form onSubmit={submit} className="flex rounded-md border border-border bg-white shadow-sm dark:bg-slate-950">
        <Search className="ml-3 mt-2.5 h-4 w-4 text-slate-400" />
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search nodes, assets, incidents, documents"
          className="h-10 min-w-0 flex-1 bg-transparent px-3 text-sm outline-none"
        />
      </form>
      {results.length ? (
        <div className="mt-2 max-h-72 overflow-auto rounded-md border border-border bg-white shadow-lg dark:bg-slate-950">
          {results.map((node) => (
            <button
              key={node.id}
              onClick={() => onSelect(node)}
              className="block w-full border-b border-border px-3 py-2 text-left text-sm last:border-b-0 hover:bg-slate-50 dark:hover:bg-slate-900"
            >
              <span className="font-semibold">{String(node.properties.name ?? node.properties.equipment_id ?? node.id)}</span>
              <span className="ml-2 text-xs text-slate-500 dark:text-slate-400">{node.labels.join(", ")}</span>
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}

