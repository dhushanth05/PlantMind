import { motion } from "framer-motion";
import { Filter, GitBranch, Search, Wrench, X } from "lucide-react";
import { useDeferredValue, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { SectionCard } from "@/components/dashboard/SectionCard";
import { EmptyState } from "@/components/shared/EmptyState";
import { ErrorState } from "@/components/shared/ErrorState";
import { LoadingState } from "@/components/shared/LoadingState";
import { cn } from "@/lib/utils";

import { useAlertsDashboard } from "./hooks";
import type { AlertRecord, AlertSeverity, AlertStatus } from "./types";

const severityStyles: Record<AlertSeverity, string> = {
  Low: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200",
  Medium: "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
  High: "bg-orange-50 text-orange-700 dark:bg-orange-950/40 dark:text-orange-300",
  Critical: "bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300",
};

const severities: Array<"All" | AlertSeverity> = ["All", "Low", "Medium", "High", "Critical"];
const statuses: Array<"All" | AlertStatus> = ["All", "Open", "Acknowledged", "Resolved"];

export function AlertsCenterPage() {
  const { data, isLoading, isError } = useAlertsDashboard();
  const [query, setQuery] = useState("");
  const [severity, setSeverity] = useState<"All" | AlertSeverity>("All");
  const [status, setStatus] = useState<"All" | AlertStatus>("All");
  const [selected, setSelected] = useState<AlertRecord | undefined>();
  const deferredQuery = useDeferredValue(query);

  const alerts = useMemo(() => {
    const all = [...(data?.active_alerts ?? []), ...(data?.alert_history ?? [])];
    return all.filter((alert) => {
      const haystack = `${alert.title} ${alert.asset_id ?? ""} ${alert.failure_mode ?? ""}`.toLowerCase();
      return (
        haystack.includes(deferredQuery.toLowerCase()) &&
        (severity === "All" || alert.severity === severity) &&
        (status === "All" || alert.status === status)
      );
    });
  }, [data, deferredQuery, severity, status]);

  if (isLoading) return <LoadingState label="Loading Alerts Center" />;
  if (isError || !data) return <ErrorState message="Unable to load alerts center." />;

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <header className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <p className="text-sm font-medium text-primary">Alerts Center</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">Operational alert triage</h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-600 dark:text-slate-300">
            Active alerts, incident-linked history, severity filters, and asset context navigation.
          </p>
        </div>
        <div className="grid gap-2 sm:grid-cols-4">
          <Metric label="Active" value={data.summary.active} />
          <Metric label="Critical" value={data.summary.critical} />
          <Metric label="High" value={data.summary.high} />
          <Metric label="Resolved" value={data.summary.resolved} />
        </div>
      </header>

      <SectionCard title="Alert workbench" description="Search and filter active and historical alerts">
        <div className="mb-4 grid gap-3 xl:grid-cols-[1fr_180px_180px]">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search alerts, assets, failure modes"
              className="h-10 w-full rounded-md border border-border bg-white pl-9 pr-3 text-sm outline-none focus:border-primary dark:bg-slate-950"
            />
          </div>
          <Select value={severity} values={severities} onChange={(value) => setSeverity(value as "All" | AlertSeverity)} />
          <Select value={status} values={statuses} onChange={(value) => setStatus(value as "All" | AlertStatus)} />
        </div>

        {alerts.length ? (
          <div className="overflow-hidden rounded-md border border-border">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500 dark:bg-slate-900 dark:text-slate-400">
                <tr>
                  <th className="px-3 py-2 font-medium">Alert</th>
                  <th className="px-3 py-2 font-medium">Severity</th>
                  <th className="px-3 py-2 font-medium">Asset</th>
                  <th className="px-3 py-2 font-medium">Failure Mode</th>
                  <th className="px-3 py-2 font-medium">Status</th>
                  <th className="px-3 py-2 font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert) => (
                  <tr key={alert.id} className="cursor-pointer border-t border-border hover:bg-slate-50 dark:hover:bg-slate-900" onClick={() => setSelected(alert)}>
                    <td className="px-3 py-2 font-medium">{alert.title}</td>
                    <td className="px-3 py-2"><span className={cn("rounded px-2 py-1 text-xs font-medium", severityStyles[alert.severity])}>{alert.severity}</span></td>
                    <td className="px-3 py-2 text-slate-600 dark:text-slate-300">{alert.asset_id ?? "Plant"}</td>
                    <td className="px-3 py-2 text-slate-600 dark:text-slate-300">{alert.failure_mode ?? "N/A"}</td>
                    <td className="px-3 py-2">{alert.status}</td>
                    <td className="px-3 py-2 text-slate-500 dark:text-slate-400">{alert.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState title="No alerts found" description="No active or historical alerts match the current filters." />
        )}
      </SectionCard>

      <AlertDrawer alert={selected} onClose={() => setSelected(undefined)} />
    </motion.div>
  );
}

function AlertDrawer({ alert, onClose }: { alert?: AlertRecord; onClose: () => void }) {
  if (!alert) return null;
  return (
    <aside className="fixed bottom-0 right-0 top-0 z-50 w-full overflow-auto border-l border-border bg-white p-5 shadow-xl dark:bg-slate-950 sm:w-[420px]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase text-primary">Alert Details</p>
          <h2 className="mt-1 text-lg font-semibold">{alert.title}</h2>
        </div>
        <button onClick={onClose} className="inline-flex h-8 w-8 items-center justify-center rounded-md hover:bg-slate-100 dark:hover:bg-slate-900">
          <X className="h-4 w-4" />
        </button>
      </div>
      <div className="mt-5 space-y-3">
        <Detail label="Severity" value={alert.severity} />
        <Detail label="Status" value={alert.status} />
        <Detail label="Asset" value={alert.asset_id ?? "Plant"} />
        <Detail label="Failure Mode" value={alert.failure_mode ?? "N/A"} />
        <Detail label="Timestamp" value={alert.timestamp} />
        {alert.description ? <p className="rounded-md border border-border p-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{alert.description}</p> : null}
        <div className="grid gap-2">
          {alert.asset_id ? (
            <Link to={`/assets/${encodeURIComponent(alert.asset_id)}`} className="inline-flex h-9 items-center justify-center gap-2 rounded-md bg-primary px-3 text-sm font-medium text-white">
              <Wrench className="h-4 w-4" /> Open Digital Twin
            </Link>
          ) : null}
          <Link to={`/graph?node=${encodeURIComponent(alert.asset_id ?? alert.incident_id ?? alert.id)}`} className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-border px-3 text-sm font-medium">
            <GitBranch className="h-4 w-4" /> Open in Graph
          </Link>
        </div>
      </div>
    </aside>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border p-3">
      <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-1 text-sm font-semibold">{value}</p>
    </div>
  );
}

function Select({ value, values, onChange }: { value: string; values: string[]; onChange: (value: string) => void }) {
  return (
    <label className="relative">
      <Filter className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
      <select value={value} onChange={(event) => onChange(event.target.value)} className="h-10 w-full rounded-md border border-border bg-white pl-9 pr-3 text-sm outline-none focus:border-primary dark:bg-slate-950">
        {values.map((item) => <option key={item}>{item}</option>)}
      </select>
    </label>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-border bg-white px-4 py-2 text-center shadow-sm dark:bg-slate-950">
      <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
      <p className="text-lg font-semibold">{value}</p>
    </div>
  );
}
