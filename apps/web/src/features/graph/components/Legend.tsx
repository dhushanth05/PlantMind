import { nodeTypeConfig } from "../graph-utils";
import type { GraphNodeType } from "../types";

const labels: GraphNodeType[] = ["Equipment", "Document", "Incident", "Procedure", "Person", "FailureMode"];

export function Legend() {
  return (
    <div className="absolute bottom-4 left-4 z-10 rounded-md border border-border bg-white p-3 shadow-sm dark:bg-slate-950">
      <p className="text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">Legend</p>
      <div className="mt-2 grid grid-cols-2 gap-2">
        {labels.map((label) => {
          const config = nodeTypeConfig[label];
          const Icon = config.icon;
          return (
            <div key={label} className="flex items-center gap-2 text-xs">
              <span className="flex h-5 w-5 items-center justify-center rounded" style={{ background: config.bg, color: config.color }}>
                <Icon className="h-3 w-3" />
              </span>
              {label === "FailureMode" ? "Failure Mode" : label}
            </div>
          );
        })}
      </div>
    </div>
  );
}

