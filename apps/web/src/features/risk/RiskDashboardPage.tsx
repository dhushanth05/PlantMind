import { motion } from "framer-motion";
import {
  AlertTriangle,
  ArrowRight,
  CalendarClock,
  Grid3X3,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";
import { Link } from "react-router-dom";

import { SectionCard } from "@/components/dashboard/SectionCard";
import { EmptyState } from "@/components/shared/EmptyState";
import { ErrorState } from "@/components/shared/ErrorState";
import { LoadingState } from "@/components/shared/LoadingState";
import { cn } from "@/lib/utils";

import { useRiskDashboard } from "./hooks";
import type { RiskAlert, RiskAsset, RiskFailureMode, RiskHeatmapCell, RiskLevel, RiskRecommendation, RiskTimelineEvent } from "./types";

const riskStyles: Record<RiskLevel, string> = {
  Low: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300",
  Medium: "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
  High: "bg-orange-50 text-orange-700 dark:bg-orange-950/40 dark:text-orange-300",
  Critical: "bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300",
};

export function RiskDashboardPage() {
  const { data, isLoading, isError } = useRiskDashboard();

  if (isLoading) {
    return <LoadingState label="Loading Risk Intelligence" />;
  }

  if (isError || !data) {
    return <ErrorState message="Unable to load risk intelligence." />;
  }

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <header className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <p className="text-sm font-medium text-primary">Risk Intelligence Center</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">Executive operational risk</h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-600 dark:text-slate-300">
            Asset risk, recurring failures, alerts, recommendations, and incident chronology from the live PlantMind backend.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <MetricPill icon={<ShieldAlert className="h-4 w-4" />} label="Overall" value={data.overall_risk.level} tone={data.overall_risk.level} />
          <MetricPill icon={<TrendingUp className="h-4 w-4" />} label="Score" value={String(data.risk_score)} />
          <MetricPill icon={<AlertTriangle className="h-4 w-4" />} label="Open Alerts" value={String(data.alerts.length)} />
        </div>
      </header>

      <section className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
        <SectionCard title="Overall risk score" description="Current aggregate exposure across assets, failures, alerts, and incidents">
          <div className="flex items-end justify-between gap-5">
            <div>
              <p className="text-xs uppercase text-slate-500 dark:text-slate-400">Score</p>
              <p className="mt-1 text-5xl font-semibold">{data.risk_score}</p>
              <span className={cn("mt-3 inline-flex rounded px-2 py-1 text-xs font-medium", riskStyles[data.overall_risk.level])}>
                {data.overall_risk.level}
              </span>
            </div>
            <div className="flex h-20 items-end gap-1.5">
              {data.overall_risk.trend.map((value, index) => (
                <span key={index} className="w-3 rounded-sm bg-primary/75" style={{ height: `${Math.max(8, value)}%` }} />
              ))}
            </div>
          </div>
          <p className="mt-5 text-sm leading-6 text-slate-600 dark:text-slate-300">{data.overall_risk.explanation}</p>
        </SectionCard>

        <RiskHeatmap cells={data.heatmap} />
      </section>

      <section className="grid gap-5 xl:grid-cols-3">
        <HighRiskAssets assets={data.high_risk_assets} />
        <FailureModes failureModes={data.recurring_failure_modes} />
        <OpenAlerts alerts={data.alerts} />
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
        <Recommendations recommendations={data.recommendations} />
        <IncidentTimeline events={data.timeline} />
      </section>
    </motion.div>
  );
}

function HighRiskAssets({ assets }: { assets: RiskAsset[] }) {
  return (
    <SectionCard title="High risk assets" description="Assets ranked by graph criticality and incident evidence">
      {assets.length ? (
        <div className="space-y-3">
          {assets.map((asset) => (
            <Link key={asset.equipment_id} to={`/assets/${encodeURIComponent(asset.equipment_id)}`} className="block rounded-md border border-border p-3 transition hover:border-primary hover:bg-slate-50 dark:hover:bg-slate-900">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold">{asset.name || asset.equipment_id}</p>
                  <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                    {asset.incident_count} incidents / {asset.failure_mode_count} failure modes
                  </p>
                </div>
                <span className={cn("rounded px-2 py-1 text-xs font-medium", riskStyles[asset.risk_level])}>{asset.risk_score}</span>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState title="No high risk assets" description="High-risk asset rankings appear after graph analytics are available." />
      )}
    </SectionCard>
  );
}

function FailureModes({ failureModes }: { failureModes: RiskFailureMode[] }) {
  return (
    <SectionCard title="Recurring failure modes" description="Failure modes with repeated evidence in graph context">
      {failureModes.length ? (
        <div className="space-y-3">
          {failureModes.map((mode) => (
            <div key={mode.failure_mode} className="rounded-md border border-border p-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold">{mode.failure_mode}</p>
                  <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{mode.mentions} mentions</p>
                </div>
                <span className={cn("rounded px-2 py-1 text-xs font-medium", riskStyles[mode.severity])}>{mode.severity}</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState title="No recurring failures" description="Failure modes will appear after graph relationships are built." />
      )}
    </SectionCard>
  );
}

function OpenAlerts({ alerts }: { alerts: RiskAlert[] }) {
  return (
    <SectionCard title="Open alerts" description="High-priority operational risk signals">
      {alerts.length ? (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <Link key={alert.id} to={`/alerts?incidentId=${encodeURIComponent(alert.incident_id ?? alert.id)}`} className="block rounded-md border border-border p-3 transition hover:border-primary hover:bg-slate-50 dark:hover:bg-slate-900">
              <div className="flex items-start gap-3">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-3">
                    <p className="truncate text-sm font-semibold">{alert.title}</p>
                    <span className={cn("rounded px-2 py-0.5 text-xs font-medium", riskStyles[alert.severity])}>{alert.severity}</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{alert.asset_id ?? "Plant"} / {alert.timestamp}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState title="No open alerts" description="No high-priority risk alerts are currently available." />
      )}
    </SectionCard>
  );
}

function Recommendations({ recommendations }: { recommendations: RiskRecommendation[] }) {
  return (
    <SectionCard title="Recommendations" description="Suggested risk investigations and mitigations">
      {recommendations.length ? (
        <div className="space-y-3">
          {recommendations.map((recommendation) => (
            <Link key={recommendation.id} to={`/copilot?message=${encodeURIComponent(recommendation.copilot_query)}`} className="block rounded-md border border-border p-3 transition hover:border-primary hover:bg-slate-50 dark:hover:bg-slate-900">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold">{recommendation.title}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{recommendation.rationale}</p>
                </div>
                <span className={cn("rounded px-2 py-1 text-xs font-medium", riskStyles[recommendation.priority])}>{recommendation.priority}</span>
              </div>
              <span className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-primary">
                Ask Copilot <ArrowRight className="h-3 w-3" />
              </span>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState title="No recommendations" description="Recommendations appear when risk evidence exists." />
      )}
    </SectionCard>
  );
}

function IncidentTimeline({ events }: { events: RiskTimelineEvent[] }) {
  return (
    <SectionCard title="Incident timeline" description="Recent incident, inspection, and risk events">
      {events.length ? (
        <div className="space-y-3">
          {events.map((event) => (
            <Link key={event.id} to={`/alerts?incidentId=${encodeURIComponent(event.incident_id ?? event.id)}`} className="grid gap-3 rounded-md border border-border p-3 transition hover:border-primary hover:bg-slate-50 dark:hover:bg-slate-900 sm:grid-cols-[150px_1fr]">
              <div>
                <span className={cn("inline-flex items-center gap-2 rounded px-2 py-1 text-xs font-medium", riskStyles[event.severity])}>
                  <CalendarClock className="h-3.5 w-3.5" />
                  {event.event_type}
                </span>
                <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">{event.timestamp}</p>
              </div>
              <div>
                <p className="text-sm font-semibold">{event.title}</p>
                <p className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">{event.description}</p>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState title="No incident timeline" description="Timeline events appear after incident or asset event ingestion." />
      )}
    </SectionCard>
  );
}

function RiskHeatmap({ cells }: { cells: RiskHeatmapCell[] }) {
  return (
    <SectionCard title="Risk heatmap" description="Asset-to-failure risk intensity">
      {cells.length ? (
        <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
          {cells.map((cell) => (
            <Link key={`${cell.asset_id}-${cell.failure_mode}`} to={`/assets/${encodeURIComponent(cell.asset_id)}`} className={cn("rounded-md border border-border p-3 transition hover:border-primary", riskStyles[cell.level])}>
              <div className="flex items-center justify-between gap-3">
                <Grid3X3 className="h-4 w-4" />
                <span className="text-xs font-semibold">{cell.score}</span>
              </div>
              <p className="mt-3 truncate text-sm font-semibold">{cell.asset_name || cell.asset_id}</p>
              <p className="mt-1 truncate text-xs opacity-80">{cell.failure_mode}</p>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState title="No heatmap data" description="Heatmap cells appear when high-risk assets and failure modes overlap." />
      )}
    </SectionCard>
  );
}

function MetricPill({ icon, label, value, tone }: { icon: React.ReactNode; label: string; value: string; tone?: RiskLevel }) {
  return (
    <div className={cn("inline-flex min-w-40 items-center gap-3 rounded-md border border-border bg-white px-3 py-2 shadow-sm dark:bg-slate-950", tone && riskStyles[tone])}>
      <span>{icon}</span>
      <span>
        <span className="block text-xs opacity-75">{label}</span>
        <span className="text-sm font-semibold">{value}</span>
      </span>
    </div>
  );
}
