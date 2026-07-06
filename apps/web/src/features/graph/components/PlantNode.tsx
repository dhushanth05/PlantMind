import { Handle, Position } from "@xyflow/react";

import { cn } from "@/lib/utils";

import { nodeTypeConfig, type PlantNodeProps } from "../graph-utils";

export function PlantNode({ data, selected }: PlantNodeProps) {
  const config = nodeTypeConfig[data.type];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        "min-w-48 rounded-md border bg-white px-3 py-2 shadow-sm transition duration-200 dark:bg-slate-950",
        selected || data.highlighted ? "scale-[1.02] border-primary shadow-lg" : "border-border",
        data.dimmed && "opacity-35",
      )}
    >
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <div className="flex items-center gap-2">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md" style={{ background: config.bg, color: config.color }}>
          <Icon className="h-4 w-4" />
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-slate-950 dark:text-white">{data.label}</p>
          <p className="truncate text-xs text-slate-500 dark:text-slate-400">{data.subtitle}</p>
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
    </div>
  );
}

