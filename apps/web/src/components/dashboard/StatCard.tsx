import { ArrowDownRight, ArrowUpRight } from "lucide-react";

import type { DashboardStat } from "@/features/dashboard/api/dashboard";
import { cn } from "@/lib/utils";

const toneStyles = {
  neutral: "text-slate-600 bg-slate-100 dark:bg-slate-900 dark:text-slate-300",
  good: "text-emerald-700 bg-emerald-50 dark:bg-emerald-950/40 dark:text-emerald-300",
  warning: "text-amber-700 bg-amber-50 dark:bg-amber-950/40 dark:text-amber-300",
  danger: "text-red-700 bg-red-50 dark:bg-red-950/40 dark:text-red-300",
};

export function StatCard({ stat }: { stat: DashboardStat }) {
  const isPositive = stat.tone === "good";

  return (
    <article className="rounded-md border border-border bg-white p-4 shadow-sm dark:bg-slate-950">
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium uppercase text-slate-500 dark:text-slate-400">{stat.label}</p>
        <span className={cn("inline-flex items-center gap-1 rounded px-2 py-1 text-xs font-medium", toneStyles[stat.tone])}>
          {isPositive ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
          {stat.delta}
        </span>
      </div>
      <div className="mt-5 flex items-end justify-between gap-3">
        <p className="text-2xl font-semibold tracking-normal">{stat.value}</p>
        <div className="flex h-8 items-end gap-1">
          {stat.trend.map((value, index) => (
            <span
              key={`${stat.label}-${index}`}
              className="w-1.5 rounded-sm bg-primary/70"
              style={{ height: `${Math.max(8, value / 1.1)}%` }}
            />
          ))}
        </div>
      </div>
    </article>
  );
}
