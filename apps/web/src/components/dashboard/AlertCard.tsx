import { AlertTriangle } from "lucide-react";

import type { AlertItem } from "@/features/dashboard/api/dashboard";
import { cn } from "@/lib/utils";

const severityStyles = {
  Low: "bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-300",
  Medium: "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
  High: "bg-orange-50 text-orange-700 dark:bg-orange-950/40 dark:text-orange-300",
  Critical: "bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300",
};

export function AlertCard({ alert }: { alert: AlertItem }) {
  return (
    <article className="flex gap-3 rounded-md border border-border p-3">
      <div className="mt-0.5 flex h-8 w-8 items-center justify-center rounded-md bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300">
        <AlertTriangle className="h-4 w-4" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-3">
          <p className="truncate text-sm font-semibold">{alert.asset}</p>
          <span className={cn("rounded px-2 py-0.5 text-xs font-medium", severityStyles[alert.severity])}>{alert.severity}</span>
        </div>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{alert.title}</p>
        <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">{alert.timestamp}</p>
      </div>
    </article>
  );
}
