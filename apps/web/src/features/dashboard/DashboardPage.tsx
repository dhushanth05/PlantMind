import { motion } from "framer-motion";
import { ArrowRight, FileText, GitBranch, ShieldAlert, Upload, Wrench } from "lucide-react";
import { Link } from "react-router-dom";

import { ActivityCard } from "@/components/dashboard/ActivityCard";
import { AlertCard } from "@/components/dashboard/AlertCard";
import { SectionCard } from "@/components/dashboard/SectionCard";
import { StatCard } from "@/components/dashboard/StatCard";
import { EmptyState } from "@/components/shared/EmptyState";
import { ErrorState } from "@/components/shared/ErrorState";
import { LoadingState } from "@/components/shared/LoadingState";
import type { CriticalEquipment, FrequentFailureMode, RecentUpload } from "@/features/dashboard/api/dashboard";
import { useDashboardData } from "@/features/dashboard/hooks";

export function DashboardPage() {
  const { data, isLoading, isError } = useDashboardData();

  if (isLoading) {
    return <LoadingState />;
  }

  if (isError || !data) {
    return <ErrorState message="Unable to load dashboard telemetry." />;
  }

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-medium text-primary">Operations dashboard</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">Plant intelligence overview</h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-600 dark:text-slate-300">
            Live operational knowledge, graph intelligence, asset risk, and ingestion activity across the plant.
          </p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/documents"
            className="inline-flex h-9 items-center gap-2 rounded-md bg-primary px-3 text-sm font-medium text-white"
          >
            <Upload className="h-4 w-4" />
            Upload
          </Link>
          <Link
            to="/graph"
            className="inline-flex h-9 items-center gap-2 rounded-md border border-border bg-white px-3 text-sm font-medium dark:bg-slate-950"
          >
            <GitBranch className="h-4 w-4" />
            Open Graph
          </Link>
        </div>
      </header>

      {data.stats.length ? (
        <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
          {data.stats.map((stat) => (
            <StatCard key={stat.label} stat={stat} />
          ))}
        </section>
      ) : (
        <EmptyState title="No dashboard metrics" description="Metrics will appear after documents, graph nodes, or alerts are indexed." />
      )}

      <section className="grid gap-5 xl:grid-cols-[1.3fr_0.7fr]">
        <SectionCard title="Knowledge graph" description="Entity clusters, relationship density, and graph readiness">
          {data.graph.nodes || data.graph.relationships || data.graph.clusters.length ? (
            <div className="grid gap-4 lg:grid-cols-[1fr_220px]">
              <div className="relative h-64 overflow-hidden rounded-md border border-border bg-slate-50 dark:bg-slate-900">
                <GraphPreview clusters={data.graph.clusters} />
              </div>
              <div className="space-y-3">
                <div>
                  <p className="text-xs uppercase text-slate-500 dark:text-slate-400">Nodes</p>
                  <p className="mt-1 text-2xl font-semibold">{data.graph.nodes.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs uppercase text-slate-500 dark:text-slate-400">Relationships</p>
                  <p className="mt-1 text-2xl font-semibold">{data.graph.relationships.toLocaleString()}</p>
                </div>
                <div className="space-y-2">
                  {data.graph.clusters.map((cluster) => (
                    <div key={cluster.label}>
                      <div className="flex justify-between text-xs">
                        <span>{cluster.label}</span>
                        <span>{cluster.value}%</span>
                      </div>
                      <div className="mt-1 h-1.5 rounded-full bg-slate-100 dark:bg-slate-800">
                        <div className="h-1.5 rounded-full bg-primary" style={{ width: `${cluster.value}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <EmptyState title="No graph data" description="Upload documents to create entities and relationships." />
          )}
        </SectionCard>

        <SectionCard title="Recent alerts" description="Prioritized operational signals">
          <div className="space-y-3">
            {data.alerts.length ? (
              data.alerts.map((alert) => <AlertCard key={alert.id} alert={alert} />)
            ) : (
              <EmptyState title="No alerts" description="All monitored assets are currently quiet." />
            )}
          </div>
        </SectionCard>
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
        <SectionCard title="Risk score" description="Current aggregate exposure from alerts, incidents, and graph criticality">
          <div className="rounded-md border border-border bg-slate-50 p-4 dark:bg-slate-900">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase text-slate-500 dark:text-slate-400">Plant risk</p>
                <p className="mt-2 text-4xl font-semibold">{data.risk.score}</p>
              </div>
              <span className="rounded bg-amber-50 px-2 py-1 text-xs font-medium text-amber-700 dark:bg-amber-950/40 dark:text-amber-300">
                {data.risk.level}
              </span>
            </div>
            <p className="mt-4 text-sm leading-6 text-slate-600 dark:text-slate-300">{data.risk.explanation}</p>
          </div>
        </SectionCard>

        <SectionCard title="Recent activity" description="Pipeline, graph, alert, and asset events">
          <div>
            {data.activities.length ? (
              data.activities.map((activity) => <ActivityCard key={activity.id} activity={activity} />)
            ) : (
              <EmptyState title="No recent activity" description="Upload documents or build graph context to populate the activity stream." />
            )}
          </div>
        </SectionCard>
      </section>

      <section className="grid gap-5 xl:grid-cols-3">
        <SectionCard title="Recent uploads" description="Latest document ingestion records">
          {data.recent_uploads.length ? (
            <div className="space-y-3">
              {data.recent_uploads.map((upload) => (
                <RecentUploadRow key={upload.id} upload={upload} />
              ))}
            </div>
          ) : (
            <EmptyState title="No uploads" description="Uploaded documents will appear here after ingestion starts." />
          )}
        </SectionCard>

        <SectionCard title="Critical equipment" description="Assets ranked by incidents, failure modes, and graph centrality">
          {data.critical_equipment.length ? (
            <div className="space-y-3">
              {data.critical_equipment.map((asset) => (
                <CriticalEquipmentRow key={asset.equipment_id} asset={asset} />
              ))}
            </div>
          ) : (
            <EmptyState title="No critical assets" description="Critical equipment rankings appear once equipment is connected in the graph." />
          )}
        </SectionCard>

        <SectionCard title="Frequent failure modes" description="Failure modes with the highest graph mention counts">
          {data.frequent_failure_modes.length ? (
            <div className="space-y-3">
              {data.frequent_failure_modes.map((failureMode) => (
                <FailureModeRow key={failureMode.failure_mode} failureMode={failureMode} />
              ))}
            </div>
          ) : (
            <EmptyState title="No failure modes" description="Failure mode signals will appear after entity extraction and graph linking." />
          )}
        </SectionCard>
      </section>

      <SectionCard title="Quick actions" description="Common investigation and ingestion workflows">
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {data.quick_actions.map((action, index) => (
            <Link
              key={action.label}
              to={action.path}
              className="group rounded-md border border-border p-4 transition hover:border-primary hover:bg-slate-50 dark:hover:bg-slate-900"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-300">
                {(() => {
                  const Icon = [Upload, ShieldAlert, GitBranch, ShieldAlert][index] ?? ArrowRight;
                  return <Icon className="h-4 w-4" />;
                })()}
              </div>
              <p className="mt-3 text-sm font-semibold">{action.label}</p>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{action.description}</p>
            </Link>
          ))}
        </div>
      </SectionCard>
    </motion.div>
  );
}

function GraphPreview({ clusters }: { clusters: { label: string; value: number }[] }) {
  const nodes = (clusters.length ? clusters : [{ label: "Graph", value: 50 }]).slice(0, 5).map((cluster, index) => ({
    x: ["18%", "46%", "72%", "30%", "68%"][index] ?? "50%",
    y: ["24%", "38%", "28%", "72%", "72%"][index] ?? "50%",
    size: Math.max(34, Math.min(62, 30 + cluster.value)),
    label: cluster.label.slice(0, 4),
  }));

  return (
    <div className="absolute inset-0">
      <svg className="h-full w-full" role="img" aria-label="Knowledge graph preview">
        <line x1="18%" y1="24%" x2="46%" y2="38%" stroke="currentColor" className="text-slate-300 dark:text-slate-700" />
        <line x1="46%" y1="38%" x2="72%" y2="28%" stroke="currentColor" className="text-slate-300 dark:text-slate-700" />
        <line x1="46%" y1="38%" x2="68%" y2="72%" stroke="currentColor" className="text-slate-300 dark:text-slate-700" />
        <line x1="18%" y1="24%" x2="30%" y2="72%" stroke="currentColor" className="text-slate-300 dark:text-slate-700" />
      </svg>
      {nodes.map((node) => (
        <div
          key={node.label}
          className="absolute flex items-center justify-center rounded-full border border-white bg-primary text-xs font-semibold text-white shadow-lg"
          style={{ left: node.x, top: node.y, width: node.size, height: node.size, transform: "translate(-50%, -50%)" }}
        >
          {node.label}
        </div>
      ))}
    </div>
  );
}

function RecentUploadRow({ upload }: { upload: RecentUpload }) {
  return (
    <div className="rounded-md border border-border bg-slate-50 p-3 dark:bg-slate-900">
      <div className="flex items-start gap-3">
        <FileText className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-3">
            <p className="truncate text-sm font-semibold">{upload.document_name}</p>
            <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-200">
              {upload.status}
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{upload.timestamp}</p>
          {upload.document_id ? <p className="mt-1 truncate text-xs text-slate-500 dark:text-slate-400">{upload.document_id}</p> : null}
        </div>
      </div>
    </div>
  );
}

function CriticalEquipmentRow({ asset }: { asset: CriticalEquipment }) {
  return (
    <Link
      to={`/assets/${encodeURIComponent(asset.equipment_id)}`}
      className="block rounded-md border border-border bg-slate-50 p-3 transition hover:border-primary dark:bg-slate-900"
    >
      <div className="flex items-start gap-3">
        <Wrench className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-3">
            <p className="truncate text-sm font-semibold">{asset.name || asset.equipment_id}</p>
            <span className="text-xs font-medium text-primary">{asset.criticality_score ?? 0}</span>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            {asset.incident_count ?? 0} incidents / {asset.failure_mode_count ?? 0} failure modes / {asset.degree ?? 0} links
          </p>
        </div>
      </div>
    </Link>
  );
}

function FailureModeRow({ failureMode }: { failureMode: FrequentFailureMode }) {
  return (
    <div className="rounded-md border border-border bg-slate-50 p-3 dark:bg-slate-900">
      <div className="flex items-center justify-between gap-3">
        <p className="truncate text-sm font-semibold">{failureMode.failure_mode}</p>
        <span className="rounded bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">{failureMode.mentions}</span>
      </div>
      <div className="mt-3 h-1.5 rounded-full bg-slate-100 dark:bg-slate-800">
        <div className="h-1.5 rounded-full bg-primary" style={{ width: `${Math.min(100, Math.max(8, failureMode.mentions * 8))}%` }} />
      </div>
    </div>
  );
}
