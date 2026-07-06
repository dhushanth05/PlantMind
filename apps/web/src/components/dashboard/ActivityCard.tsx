import { AlertTriangle, FileText, GitBranch, Wrench } from "lucide-react";

import type { ActivityItem } from "@/features/dashboard/api/dashboard";

const icons = {
  document: FileText,
  graph: GitBranch,
  asset: Wrench,
  alert: AlertTriangle,
};

export function ActivityCard({ activity }: { activity: ActivityItem }) {
  const Icon = icons[activity.type];

  return (
    <article className="flex gap-3 border-b border-border py-3 last:border-b-0">
      <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-300">
        <Icon className="h-4 w-4" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-start justify-between gap-4">
          <p className="text-sm font-semibold">{activity.title}</p>
          <span className="shrink-0 text-xs text-slate-500 dark:text-slate-400">{activity.timestamp}</span>
        </div>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{activity.description}</p>
      </div>
    </article>
  );
}
