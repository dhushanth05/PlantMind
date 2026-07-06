import { ShieldCheck } from "lucide-react";

import { cn } from "@/lib/utils";

export function ConfidenceBadge({ confidence }: { confidence?: number }) {
  const value = Math.round((confidence ?? 0) * 100);
  const tone =
    value >= 85
      ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300"
      : value >= 65
        ? "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300"
        : "bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300";

  return (
    <span className={cn("inline-flex items-center gap-1 rounded px-2 py-1 text-xs font-medium", tone)}>
      <ShieldCheck className="h-3 w-3" />
      {value}% confidence
    </span>
  );
}

