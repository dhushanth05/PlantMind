import { motion } from "framer-motion";
import { BarChart3, Brain, LineChart, PieChart, TrendingUp } from "lucide-react";

import { SectionCard } from "@/components/dashboard/SectionCard";
import { EmptyState } from "@/components/shared/EmptyState";
import { ErrorState } from "@/components/shared/ErrorState";
import { LoadingState } from "@/components/shared/LoadingState";

import { useExecutiveAnalytics } from "./hooks";
import type { DistributionItem, SeriesPoint } from "./types";

export function ExecutiveAnalyticsPage() {
  const { data, isLoading, isError } = useExecutiveAnalytics();

  if (isLoading) return <LoadingState label="Loading Executive Analytics" />;
  if (isError || !data) return <ErrorState message="Unable to load executive analytics." />;

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <header>
        <p className="text-sm font-medium text-primary">Executive Analytics</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-normal">Operational intelligence trends</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-600 dark:text-slate-300">
          KPIs, knowledge growth, incident trends, asset health distribution, failure distribution, and AI summary.
        </p>
      </header>

      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {data.kpis.map((kpi) => (
          <div key={kpi.label} className="rounded-md border border-border bg-white p-4 shadow-sm dark:bg-slate-950">
            <p className="text-xs uppercase text-slate-500 dark:text-slate-400">{kpi.label}</p>
            <p className="mt-4 text-2xl font-semibold">{kpi.value}</p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{kpi.change}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <SeriesCard title="Knowledge growth" icon={<LineChart className="h-4 w-4" />} points={data.knowledge_growth} />
        <SeriesCard title="Incident trends" icon={<TrendingUp className="h-4 w-4" />} points={data.incident_trends} />
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <DistributionCard title="Asset health distribution" icon={<PieChart className="h-4 w-4" />} items={data.asset_health_distribution} />
        <DistributionCard title="Failure distribution" icon={<BarChart3 className="h-4 w-4" />} items={data.failure_distribution} />
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.7fr_1.3fr]">
        <SectionCard title="AI summary" description="Executive narrative generated from live platform metrics">
          <div className="flex gap-3 rounded-md border border-border bg-slate-50 p-4 dark:bg-slate-900">
            <Brain className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
            <p className="text-sm leading-6 text-slate-600 dark:text-slate-300">{data.ai_summary}</p>
          </div>
        </SectionCard>
        <SectionCard title="Operational insights" description="High-signal observations from risk, graph, and incident data">
          {data.operational_insights.length ? (
            <div className="grid gap-3 xl:grid-cols-2">
              {data.operational_insights.map((insight) => (
                <div key={insight.title} className="rounded-md border border-border p-4">
                  <p className="text-sm font-semibold">{insight.title}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{insight.summary}</p>
                  <p className="mt-3 text-xs font-medium text-primary">{insight.priority}</p>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title="No insights yet" description="Insights appear when graph, incident, or document data is available." />
          )}
        </SectionCard>
      </section>
    </motion.div>
  );
}

function SeriesCard({ title, icon, points }: { title: string; icon: React.ReactNode; points: SeriesPoint[] }) {
  const max = Math.max(1, ...points.map((point) => point.value));
  return (
    <SectionCard title={title} description="Six-point platform trend">
      <div className="flex items-end gap-2">
        {points.map((point) => (
          <div key={point.label} className="flex flex-1 flex-col items-center gap-2">
            <div className="flex h-40 w-full items-end rounded-md bg-slate-50 px-2 dark:bg-slate-900">
              <div className="w-full rounded-t bg-primary" style={{ height: `${Math.max(5, (point.value / max) * 100)}%` }} />
            </div>
            <span className="text-xs text-slate-500 dark:text-slate-400">{point.label}</span>
          </div>
        ))}
      </div>
      <div className="mt-3 inline-flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">{icon}{title}</div>
    </SectionCard>
  );
}

function DistributionCard({ title, icon, items }: { title: string; icon: React.ReactNode; items: DistributionItem[] }) {
  const total = Math.max(1, items.reduce((sum, item) => sum + item.value, 0));
  return (
    <SectionCard title={title} description="Current distribution across platform records">
      {items.length ? (
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.label}>
              <div className="flex justify-between text-sm">
                <span className="font-medium">{item.label}</span>
                <span>{item.value}</span>
              </div>
              <div className="mt-1 h-2 rounded-full bg-slate-100 dark:bg-slate-800">
                <div className="h-2 rounded-full bg-primary" style={{ width: `${Math.max(4, (item.value / total) * 100)}%` }} />
              </div>
            </div>
          ))}
          <div className="inline-flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">{icon}{title}</div>
        </div>
      ) : (
        <EmptyState title="No distribution data" description="Distribution appears after data is ingested." />
      )}
    </SectionCard>
  );
}
