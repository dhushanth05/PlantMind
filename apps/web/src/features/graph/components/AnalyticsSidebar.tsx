import { SectionCard } from "@/components/dashboard/SectionCard";

import type { GraphAnalytics, GraphOverview } from "../types";

type AnalyticsSidebarProps = {
  overview?: GraphOverview;
  analytics?: GraphAnalytics;
};

export function AnalyticsSidebar({ overview, analytics }: AnalyticsSidebarProps) {
  return (
    <aside className="hidden w-80 shrink-0 space-y-4 2xl:block">
      <SectionCard title="Graph statistics" description="Current Neo4j knowledge graph">
        <div className="grid grid-cols-2 gap-3">
          <Metric label="Nodes" value={(overview?.total_nodes ?? 0).toLocaleString()} />
          <Metric label="Edges" value={(overview?.total_relationships ?? 0).toLocaleString()} />
        </div>
        <div className="mt-4 space-y-2">
          {overview?.node_types.slice(0, 6).map((item) => (
            <Bar key={item.type} label={item.type} value={item.count} max={overview.node_types[0]?.count ?? item.count} />
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Most connected assets">
        <div className="space-y-2">
          {analytics?.most_connected_assets.map((asset) => (
            <RankedItem key={asset.equipment_id} title={asset.name ?? asset.equipment_id} value={`${asset.degree} links`} />
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Critical equipment">
        <div className="space-y-2">
          {analytics?.critical_equipment.map((asset) => (
            <RankedItem
              key={asset.equipment_id}
              title={asset.name ?? asset.equipment_id}
              value={`Score ${asset.criticality_score}`}
            />
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Frequent failure modes">
        <div className="space-y-2">
          {analytics?.frequent_failure_modes.map((mode) => (
            <RankedItem key={mode.failure_mode} title={mode.failure_mode} value={`${mode.mentions} mentions`} />
          ))}
        </div>
      </SectionCard>
    </aside>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border p-3">
      <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-1 text-xl font-semibold">{value}</p>
    </div>
  );
}

function Bar({ label, value, max }: { label: string; value: number; max: number }) {
  return (
    <div>
      <div className="flex justify-between text-xs">
        <span>{label}</span>
        <span>{value.toLocaleString()}</span>
      </div>
      <div className="mt-1 h-1.5 rounded-full bg-slate-100 dark:bg-slate-900">
        <div className="h-1.5 rounded-full bg-primary" style={{ width: `${Math.max(8, (value / max) * 100)}%` }} />
      </div>
    </div>
  );
}

function RankedItem({ title, value }: { title: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-md border border-border px-3 py-2 text-sm">
      <span className="truncate font-medium">{title}</span>
      <span className="shrink-0 text-xs text-slate-500 dark:text-slate-400">{value}</span>
    </div>
  );
}

