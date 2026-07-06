import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  ArrowLeft,
  Bot,
  CalendarClock,
  ClipboardCheck,
  ExternalLink,
  GitBranch,
  HardHat,
  HeartPulse,
  Search,
  ShieldAlert,
  Wrench,
} from "lucide-react";
import { useDeferredValue, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { SectionCard } from "@/components/dashboard/SectionCard";
import { EmptyState } from "@/components/shared/EmptyState";
import { ErrorState } from "@/components/shared/ErrorState";
import { LoadingState } from "@/components/shared/LoadingState";
import { cn } from "@/lib/utils";

import { getAssetDigitalTwin } from "./api";
import type { AssetDigitalTwin, DigitalTwinRecommendation, GraphNode, RelatedAsset, RiskLevel, TimelineEvent } from "./types";

const riskStyles: Record<RiskLevel, string> = {
  Low: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300",
  Medium: "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
  High: "bg-orange-50 text-orange-700 dark:bg-orange-950/40 dark:text-orange-300",
  Critical: "bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300",
};

export function AssetDigitalTwinPage() {
  const { assetId } = useParams();
  const [documentSearch, setDocumentSearch] = useState("");
  const deferredSearch = useDeferredValue(documentSearch);

  const twinQuery = useQuery({
    queryKey: ["assets", "digital-twin", assetId],
    queryFn: () => getAssetDigitalTwin(assetId ?? ""),
    enabled: Boolean(assetId),
  });

  if (!assetId) {
    return <ErrorState message="Asset ID is required to load a digital twin." />;
  }

  if (twinQuery.isLoading) {
    return <LoadingState label="Loading Digital Twin" />;
  }

  if (twinQuery.isError || !twinQuery.data) {
    return <ErrorState message={`Unable to load digital twin for ${assetId}.`} />;
  }

  const twin = twinQuery.data;
  const assetName = getNodeName(twin.asset);
  const equipmentType = getProperty(twin.asset, "type") ?? getProperty(twin.asset, "equipment_type") ?? twin.asset.labels[0] ?? "Equipment";
  const status = getProperty(twin.asset, "status") ?? twin.health_score.status;
  const lastInspection = latestEvent(twin.operational_timeline, "Inspection") ?? latestEvent(twin.maintenance_history, "Inspection");
  const lastMaintenance = latestEvent(twin.operational_timeline, "Maintenance") ?? latestEvent(twin.maintenance_history, "Maintenance");
  const filteredDocuments = twin.connected_documents.filter((document) =>
    getNodeName(document).toLowerCase().includes(deferredSearch.toLowerCase()),
  );

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <header className="rounded-md border border-border bg-white p-4 shadow-sm dark:bg-slate-950">
        <Link to="/assets" className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-primary dark:text-slate-300">
          <ArrowLeft className="h-4 w-4" />
          Assets
        </Link>
        <div className="mt-4 flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="text-sm font-medium text-primary">Asset Digital Twin</p>
            <h1 className="mt-1 text-2xl font-semibold tracking-normal">{assetName}</h1>
            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              <Badge>{String(equipmentType)}</Badge>
              <Badge>{assetId}</Badge>
              <Badge>Status: {String(status)}</Badge>
            </div>
          </div>
          <div className="grid gap-2 sm:grid-cols-2 xl:flex">
            <ScorePill icon={<HeartPulse className="h-4 w-4" />} label="Health" value={`${twin.health_score.score}`} />
            <ScorePill icon={<ShieldAlert className="h-4 w-4" />} label="Risk" value={twin.risk_level.level} tone={twin.risk_level.level} />
            <Link
              to={`/graph?node=${encodeURIComponent(assetId)}`}
              className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-border bg-white px-3 text-sm font-medium dark:bg-slate-950"
            >
              <GitBranch className="h-4 w-4" />
              Open Graph
            </Link>
            <Link
              to={`/copilot?asset=${encodeURIComponent(assetId)}`}
              className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-primary px-3 text-sm font-medium text-white"
            >
              <Bot className="h-4 w-4" />
              Ask AI
            </Link>
          </div>
        </div>
      </header>

      <section className="grid gap-5 xl:grid-cols-[0.7fr_0.7fr_1fr]">
        <HealthCard twin={twin} lastInspection={lastInspection} lastMaintenance={lastMaintenance} />
        <RiskCard twin={twin} />
        <GraphSummaryCard twin={twin} />
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.25fr_0.75fr]">
        <TimelineCard events={twin.operational_timeline.length ? twin.operational_timeline : twin.maintenance_history} />
        <RecommendationsCard recommendations={twin.recommendations} />
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        <FailureModesCard failureModes={twin.failure_modes} />
        <PersonnelCard personnel={twin.assigned_personnel} />
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <DocumentsCard documents={filteredDocuments} search={documentSearch} onSearch={setDocumentSearch} />
        <RelatedAssetsCard assets={twin.related_assets} />
      </section>
    </motion.div>
  );
}

function HealthCard({
  twin,
  lastInspection,
  lastMaintenance,
}: {
  twin: AssetDigitalTwin;
  lastInspection?: TimelineEvent;
  lastMaintenance?: TimelineEvent;
}) {
  const trend = [54, 62, 58, 70, 74, twin.health_score.score];

  return (
    <SectionCard title="Health" description="Current asset health and recent maintenance signals">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase text-slate-500 dark:text-slate-400">Score</p>
          <p className="mt-1 text-4xl font-semibold">{twin.health_score.score}</p>
          <p className="mt-1 text-sm font-medium text-primary">{twin.health_score.status}</p>
        </div>
        <div className="flex h-16 items-end gap-1">
          {trend.map((value, index) => (
            <span key={index} className="w-2 rounded-sm bg-primary/75" style={{ height: `${Math.max(10, value)}%` }} />
          ))}
        </div>
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <MiniMetric icon={<ClipboardCheck className="h-4 w-4" />} label="Last Inspection" value={formatDate(lastInspection?.timestamp)} />
        <MiniMetric icon={<Wrench className="h-4 w-4" />} label="Last Maintenance" value={formatDate(lastMaintenance?.timestamp)} />
      </div>
    </SectionCard>
  );
}

function RiskCard({ twin }: { twin: AssetDigitalTwin }) {
  const factors = [
    `${twin.incidents.length} connected incidents`,
    `${twin.failure_modes.length} failure modes`,
    `${twin.graph_summary.connected_nodes} connected graph nodes`,
  ];

  return (
    <SectionCard title="Risk" description="Risk level and contributing factors">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase text-slate-500 dark:text-slate-400">Level</p>
          <p className="mt-1 text-3xl font-semibold">{twin.risk_level.level}</p>
        </div>
        <span className={cn("rounded px-2 py-1 text-xs font-medium", riskStyles[twin.risk_level.level])}>{twin.risk_level.score}/100</span>
      </div>
      <p className="mt-4 text-sm leading-6 text-slate-600 dark:text-slate-300">{twin.risk_level.explanation}</p>
      <div className="mt-4 space-y-2">
        {factors.map((factor) => (
          <div key={factor} className="flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm">
            <AlertTriangle className="h-4 w-4 text-amber-600" />
            {factor}
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

function GraphSummaryCard({ twin }: { twin: AssetDigitalTwin }) {
  const metrics = [
    { label: "Connected Nodes", value: twin.graph_summary.connected_nodes },
    { label: "Documents", value: twin.graph_summary.connected_documents },
    { label: "Procedures", value: twin.graph_summary.procedures },
    { label: "Incidents", value: twin.incidents.length },
  ];

  return (
    <SectionCard title="Graph summary" description="Knowledge graph context around this asset">
      <div className="grid gap-3 sm:grid-cols-2">
        {metrics.map((metric) => (
          <div key={metric.label} className="rounded-md border border-border bg-slate-50 p-3 dark:bg-slate-900">
            <p className="text-xs text-slate-500 dark:text-slate-400">{metric.label}</p>
            <p className="mt-1 text-2xl font-semibold">{metric.value.toLocaleString()}</p>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

function TimelineCard({ events }: { events: TimelineEvent[] }) {
  return (
    <SectionCard title="Maintenance timeline" description="Chronological inspection, maintenance, repair, incident, and recommendation events">
      {events.length ? (
        <div className="space-y-3">
          {events.map((event, index) => (
            <div key={`${event.title}-${index}`} className="grid gap-3 rounded-md border border-border p-3 sm:grid-cols-[140px_1fr]">
              <div>
                <span className="inline-flex items-center gap-2 rounded bg-slate-100 px-2 py-1 text-xs font-medium dark:bg-slate-900">
                  <CalendarClock className="h-3.5 w-3.5" />
                  {event.event_type}
                </span>
                <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">{formatDate(event.timestamp)}</p>
              </div>
              <div>
                <p className="text-sm font-semibold">{event.title}</p>
                <p className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">{event.description}</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState title="No timeline events" description="Operational events will appear when maintenance and incident data is connected." />
      )}
    </SectionCard>
  );
}

function FailureModesCard({ failureModes }: { failureModes: GraphNode[] }) {
  return (
    <SectionCard title="Failure modes" description="Known failure modes linked to this asset">
      {failureModes.length ? (
        <div className="space-y-3">
          {failureModes.map((mode) => (
            <div key={mode.id} className="rounded-md border border-border p-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold">{getNodeName(mode)}</p>
                  <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Last seen: {formatUnknown(getProperty(mode, "last_seen"))}</p>
                </div>
                <span className="rounded bg-red-50 px-2 py-1 text-xs font-medium text-red-700 dark:bg-red-950/40 dark:text-red-300">
                  {formatUnknown(getProperty(mode, "severity"))}
                </span>
              </div>
              <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">Occurrences: {formatUnknown(getProperty(mode, "occurrences"))}</p>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState title="No failure modes" description="Failure modes will appear after graph extraction links them to this asset." />
      )}
    </SectionCard>
  );
}

function DocumentsCard({
  documents,
  search,
  onSearch,
}: {
  documents: GraphNode[];
  search: string;
  onSearch: (value: string) => void;
}) {
  return (
    <SectionCard
      title="Connected documents"
      description="Searchable document evidence connected to this asset"
      action={
        <div className="relative w-56">
          <Search className="pointer-events-none absolute left-2 top-2.5 h-4 w-4 text-slate-400" />
          <input
            value={search}
            onChange={(event) => onSearch(event.target.value)}
            placeholder="Search documents"
            className="h-9 w-full rounded-md border border-border bg-white pl-8 pr-3 text-sm outline-none focus:border-primary dark:bg-slate-950"
          />
        </div>
      }
    >
      {documents.length ? (
        <div className="overflow-hidden rounded-md border border-border">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500 dark:bg-slate-900 dark:text-slate-400">
              <tr>
                <th className="px-3 py-2 font-medium">Document</th>
                <th className="px-3 py-2 font-medium">Type</th>
                <th className="px-3 py-2 font-medium">Action</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((document) => (
                <tr key={document.id} className="border-t border-border">
                  <td className="px-3 py-2 font-medium">{getNodeName(document)}</td>
                  <td className="px-3 py-2 text-slate-500 dark:text-slate-400">{document.labels.join(", ")}</td>
                  <td className="px-3 py-2">
                    <Link
                      to={`/documents?documentId=${encodeURIComponent(String(getProperty(document, "document_id") ?? document.id))}`}
                      className="inline-flex items-center gap-1 text-xs font-medium text-primary"
                    >
                      Open <ExternalLink className="h-3 w-3" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <EmptyState title="No documents" description="No connected documents match the current search." />
      )}
    </SectionCard>
  );
}

function PersonnelCard({ personnel }: { personnel: GraphNode[] }) {
  return (
    <SectionCard title="Assigned personnel" description="Engineers and technicians connected to this asset">
      {personnel.length ? (
        <div className="grid gap-3 sm:grid-cols-2">
          {personnel.map((person) => (
            <div key={person.id} className="rounded-md border border-border p-3">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-md bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-300">
                  <HardHat className="h-4 w-4" />
                </div>
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold">{getNodeName(person)}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{formatUnknown(getProperty(person, "role") ?? person.labels[0])}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState title="No assigned personnel" description="Personnel assignments will appear when linked in the knowledge graph." />
      )}
    </SectionCard>
  );
}

function RecommendationsCard({ recommendations }: { recommendations: DigitalTwinRecommendation[] }) {
  return (
    <SectionCard title="Recommendations" description="AI recommendations returned by the digital twin service">
      {recommendations.length ? (
        <div className="space-y-3">
          {recommendations.map((recommendation) => (
            <div key={recommendation.title} className="rounded-md border border-border p-3">
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm font-semibold">{recommendation.title}</p>
                <span className={cn("rounded px-2 py-1 text-xs font-medium", riskStyles[recommendation.priority])}>{recommendation.priority}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{recommendation.rationale}</p>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState title="No recommendations" description="AI recommendations will appear when sufficient asset evidence is available." />
      )}
    </SectionCard>
  );
}

function RelatedAssetsCard({ assets }: { assets: RelatedAsset[] }) {
  return (
    <SectionCard title="Related assets" description="Assets connected by shared procedures, failures, or context">
      {assets.length ? (
        <div className="space-y-3">
          {assets.map((asset) => (
            <Link
              key={asset.asset_id}
              to={`/assets/${encodeURIComponent(asset.asset_id)}`}
              className="block rounded-md border border-border p-3 transition hover:border-primary hover:bg-slate-50 dark:hover:bg-slate-900"
            >
              <p className="text-sm font-semibold">{asset.name || asset.asset_id}</p>
              <p className="mt-1 text-xs font-medium text-primary">{asset.relationship}</p>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{asset.reason}</p>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState title="No related assets" description="Related assets appear when the graph finds shared context." />
      )}
    </SectionCard>
  );
}

function ScorePill({ icon, label, value, tone }: { icon: React.ReactNode; label: string; value: string; tone?: RiskLevel }) {
  return (
    <div className={cn("inline-flex h-10 items-center gap-3 rounded-md border border-border bg-white px-3 dark:bg-slate-950", tone && riskStyles[tone])}>
      <span>{icon}</span>
      <span>
        <span className="block text-xs opacity-75">{label}</span>
        <span className="text-sm font-semibold">{value}</span>
      </span>
    </div>
  );
}

function MiniMetric({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-slate-50 p-3 dark:bg-slate-900">
      <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
        {icon}
        {label}
      </div>
      <p className="mt-2 text-sm font-semibold">{value}</p>
    </div>
  );
}

function Badge({ children }: { children: React.ReactNode }) {
  return <span className="rounded bg-slate-100 px-2 py-1 font-medium text-slate-700 dark:bg-slate-900 dark:text-slate-200">{children}</span>;
}

function getNodeName(node: GraphNode) {
  return String(node.properties.name ?? node.properties.filename ?? node.properties.equipment_id ?? node.properties.document_id ?? node.id);
}

function getProperty(node: GraphNode, key: string) {
  const value = node.properties[key];
  return value === undefined || value === null ? undefined : String(value);
}

function latestEvent(events: TimelineEvent[], eventType: TimelineEvent["event_type"]) {
  return events.find((event) => event.event_type === eventType);
}

function formatDate(value?: string | null) {
  if (!value) {
    return "Not available";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(date);
}

function formatUnknown(value?: string) {
  return value && value !== "undefined" ? value : "Not available";
}
