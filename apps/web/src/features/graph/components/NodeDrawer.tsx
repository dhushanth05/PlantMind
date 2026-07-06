import { ExternalLink, X } from "lucide-react";
import { Link } from "react-router-dom";

import { SectionCard } from "@/components/dashboard/SectionCard";

import { getNodeLabel, getNodeType } from "../graph-utils";
import type { ApiGraphNode, EquipmentContext } from "../types";

type NodeDrawerProps = {
  node?: ApiGraphNode;
  equipmentContext?: EquipmentContext;
  onClose: () => void;
};

export function NodeDrawer({ node, equipmentContext, onClose }: NodeDrawerProps) {
  if (!node) return null;
  const type = getNodeType(node);
  const equipmentId = String(node.properties.equipment_id ?? node.id);
  const health = node.properties.health_score ?? (equipmentContext ? 81 : undefined);
  const risk = node.properties.risk_level ?? (equipmentContext ? "Medium" : undefined);

  return (
    <aside className="absolute right-4 top-4 z-20 hidden max-h-[calc(100%-2rem)] w-96 overflow-auto rounded-md border border-border bg-white shadow-xl dark:bg-slate-950 xl:block">
      <div className="flex items-start justify-between gap-3 border-b border-border p-4">
        <div>
          <p className="text-xs font-medium uppercase text-primary">{type === "FailureMode" ? "Failure Mode" : type}</p>
          <h2 className="mt-1 text-lg font-semibold">{getNodeLabel(node)}</h2>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{node.id}</p>
        </div>
        <button onClick={onClose} className="inline-flex h-8 w-8 items-center justify-center rounded-md hover:bg-slate-100 dark:hover:bg-slate-900">
          <X className="h-4 w-4" />
        </button>
      </div>
      <div className="space-y-4 p-4">
        <div className="grid grid-cols-2 gap-3">
          <Metric label="Health Score" value={health ? String(health) : "N/A"} />
          <Metric label="Risk Level" value={risk ? String(risk) : "N/A"} />
        </div>

        {type === "Equipment" ? (
          <Link
            to={`/assets/${encodeURIComponent(equipmentId)}`}
            className="inline-flex h-9 w-full items-center justify-center gap-2 rounded-md bg-primary px-3 text-sm font-medium text-white"
          >
            Open Digital Twin
            <ExternalLink className="h-4 w-4" />
          </Link>
        ) : null}

        <SectionCard title="Metadata">
          <dl className="space-y-2 text-sm">
            {Object.entries(node.properties).map(([key, value]) => (
              <div key={key} className="grid grid-cols-[130px_1fr] gap-2">
                <dt className="text-slate-500 dark:text-slate-400">{key}</dt>
                <dd className="min-w-0 break-words font-medium">{String(value)}</dd>
              </div>
            ))}
          </dl>
        </SectionCard>

        {equipmentContext ? (
          <>
            <NodeList title="Connected documents" nodes={equipmentContext.connected_documents} />
            <NodeList title="Connected incidents" nodes={equipmentContext.connected_incidents} />
            <NodeList title="Assigned personnel" nodes={equipmentContext.connected_personnel} />
            <NodeList title="Failure modes" nodes={equipmentContext.failure_modes} />
            <NodeList title="Procedures" nodes={equipmentContext.related_procedures} />
          </>
        ) : null}
      </div>
    </aside>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border p-3">
      <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  );
}

function NodeList({ title, nodes }: { title: string; nodes: ApiGraphNode[] }) {
  return (
    <SectionCard title={title}>
      <div className="space-y-2">
        {nodes.length ? (
          nodes.map((node) => (
            <div key={node.id} className="rounded-md border border-border px-3 py-2 text-sm">
              <p className="font-semibold">{getNodeLabel(node)}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">{node.labels.join(", ")}</p>
            </div>
          ))
        ) : (
          <p className="text-sm text-slate-500 dark:text-slate-400">No connected records found.</p>
        )}
      </div>
    </SectionCard>
  );
}
