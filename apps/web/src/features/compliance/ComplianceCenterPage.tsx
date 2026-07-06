import { motion } from "framer-motion";
import { ArrowRight, ClipboardCheck, FileWarning, Scale, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";

import { SectionCard } from "@/components/dashboard/SectionCard";
import { EmptyState } from "@/components/shared/EmptyState";
import { ErrorState } from "@/components/shared/ErrorState";
import { LoadingState } from "@/components/shared/LoadingState";
import { cn } from "@/lib/utils";

import { useComplianceDashboard } from "./hooks";
import type { ComplianceItem, ComplianceRecommendation, ComplianceSeverity, RegulatoryMapping } from "./types";

const severityStyles: Record<ComplianceSeverity, string> = {
  Low: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300",
  Medium: "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
  High: "bg-orange-50 text-orange-700 dark:bg-orange-950/40 dark:text-orange-300",
  Critical: "bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300",
};

export function ComplianceCenterPage() {
  const { data, isLoading, isError } = useComplianceDashboard();

  if (isLoading) return <LoadingState label="Loading Compliance Center" />;
  if (isError || !data) return <ErrorState message="Unable to load compliance center." />;

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <header className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <p className="text-sm font-medium text-primary">Compliance Center</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">Regulatory readiness</h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-600 dark:text-slate-300">
            SOP coverage, inspection due items, compliance gaps, and regulatory evidence mapping.
          </p>
        </div>
        <div className="grid gap-2 sm:grid-cols-2 xl:flex">
          <Metric icon={<ShieldCheck className="h-4 w-4" />} label="Score" value={String(data.overview.score)} />
          <Metric icon={<FileWarning className="h-4 w-4" />} label="Open Gaps" value={String(data.overview.open_gaps)} />
          <Metric icon={<ClipboardCheck className="h-4 w-4" />} label="Inspections Due" value={String(data.overview.inspections_due)} />
        </div>
      </header>

      <section className="grid gap-5 xl:grid-cols-[0.7fr_1.3fr]">
        <SectionCard title="Compliance overview" description="Current enterprise compliance posture">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="text-xs uppercase text-slate-500 dark:text-slate-400">Compliance score</p>
              <p className="mt-1 text-5xl font-semibold">{data.overview.score}</p>
              <p className="mt-2 text-sm font-medium text-primary">{data.overview.status}</p>
            </div>
            <div className="text-right text-sm text-slate-600 dark:text-slate-300">
              <p>{data.overview.total_documents} documents</p>
              <p>{data.overview.mapped_regulations} mapped frameworks</p>
            </div>
          </div>
        </SectionCard>
        <RegulatoryMappingCard mappings={data.regulatory_mapping} />
      </section>

      <section className="grid gap-5 xl:grid-cols-3">
        <ItemList title="Missing SOPs" description="SOP evidence gaps requiring review" items={data.missing_sops} />
        <ItemList title="Inspection due" description="Due or overdue inspection obligations" items={data.inspections_due} />
        <ItemList title="Compliance gaps" description="Open compliance exceptions and evidence gaps" items={data.compliance_gaps} />
      </section>

      <Recommendations recommendations={data.recommendations} />
    </motion.div>
  );
}

function RegulatoryMappingCard({ mappings }: { mappings: RegulatoryMapping[] }) {
  return (
    <SectionCard title="Regulatory mapping" description="OISD, PESO, Factory Act, and environmental evidence coverage">
      <div className="grid gap-3 md:grid-cols-2">
        {mappings.map((mapping) => (
          <div key={mapping.framework} className="rounded-md border border-border bg-slate-50 p-3 dark:bg-slate-900">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <Scale className="h-4 w-4 text-primary" />
                <p className="text-sm font-semibold">{mapping.framework}</p>
              </div>
              <span className="rounded bg-slate-100 px-2 py-1 text-xs font-medium dark:bg-slate-800">{mapping.status}</span>
            </div>
            <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">
              {mapping.mapped_documents} mapped documents / {mapping.gaps} gaps
            </p>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

function ItemList({ title, description, items }: { title: string; description: string; items: ComplianceItem[] }) {
  return (
    <SectionCard title={title} description={description}>
      {items.length ? (
        <div className="space-y-3">
          {items.map((item) => (
            <Link key={item.id} to={item.asset_id ? `/assets/${encodeURIComponent(item.asset_id)}` : "/documents"} className="block rounded-md border border-border p-3 transition hover:border-primary hover:bg-slate-50 dark:hover:bg-slate-900">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold">{item.title}</p>
                  <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{item.asset_id ?? item.source ?? "Plant evidence"} {item.due_date ? `/ ${item.due_date}` : ""}</p>
                </div>
                <span className={cn("rounded px-2 py-1 text-xs font-medium", severityStyles[item.severity])}>{item.severity}</span>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState title={`No ${title.toLowerCase()}`} description="No records are currently available for this category." />
      )}
    </SectionCard>
  );
}

function Recommendations({ recommendations }: { recommendations: ComplianceRecommendation[] }) {
  return (
    <SectionCard title="AI recommendations" description="Recommended compliance investigations">
      {recommendations.length ? (
        <div className="grid gap-3 xl:grid-cols-2">
          {recommendations.map((recommendation) => (
            <Link key={recommendation.id} to={`/copilot?message=${encodeURIComponent(recommendation.copilot_query)}`} className="rounded-md border border-border p-4 transition hover:border-primary hover:bg-slate-50 dark:hover:bg-slate-900">
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm font-semibold">{recommendation.title}</p>
                <span className={cn("rounded px-2 py-1 text-xs font-medium", severityStyles[recommendation.priority])}>{recommendation.priority}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{recommendation.rationale}</p>
              <span className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-primary">
                Ask Copilot <ArrowRight className="h-3 w-3" />
              </span>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState title="No recommendations" description="Recommendations appear when compliance gaps are detected." />
      )}
    </SectionCard>
  );
}

function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="inline-flex min-w-40 items-center gap-3 rounded-md border border-border bg-white px-3 py-2 shadow-sm dark:bg-slate-950">
      <span className="text-primary">{icon}</span>
      <span>
        <span className="block text-xs text-slate-500 dark:text-slate-400">{label}</span>
        <span className="text-sm font-semibold">{value}</span>
      </span>
    </div>
  );
}
