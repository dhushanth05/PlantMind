import { Network, Wrench } from "lucide-react";
import { Link } from "react-router-dom";

export function AssetCard({ asset }: { asset: string }) {
  return (
    <article className="flex items-center gap-3 rounded-md border border-border bg-white p-3 dark:bg-slate-950">
      <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-300">
        <Wrench className="h-4 w-4" />
      </div>
      <div className="min-w-0">
        <p className="truncate text-sm font-semibold">{asset}</p>
        <p className="text-xs text-slate-500 dark:text-slate-400">Related industrial asset</p>
      </div>
      <div className="ml-auto flex shrink-0 items-center gap-1">
        <Link
          to={`/assets/${encodeURIComponent(asset)}`}
          className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-border hover:bg-slate-50 dark:hover:bg-slate-900"
          title="Open Digital Twin"
        >
          <Wrench className="h-3.5 w-3.5" />
        </Link>
        <Link
          to={`/graph?q=${encodeURIComponent(asset)}`}
          className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-border hover:bg-slate-50 dark:hover:bg-slate-900"
          title="Open in Graph"
        >
          <Network className="h-3.5 w-3.5" />
        </Link>
      </div>
    </article>
  );
}
