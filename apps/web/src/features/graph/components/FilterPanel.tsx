import type { GraphFilters, GraphNodeType } from "../types";

const nodeTypes: GraphNodeType[] = ["Equipment", "Document", "Incident", "Procedure", "Person", "FailureMode"];
const relationshipTypes = ["MENTIONED_IN", "RELATED_TO", "CAUSED_BY", "ASSIGNED_TO", "REFERENCES"];

type FilterPanelProps = {
  filters: GraphFilters;
  onChange: (filters: GraphFilters) => void;
};

export function FilterPanel({ filters, onChange }: FilterPanelProps) {
  const toggleNodeType = (type: GraphNodeType) => {
    const nodeTypes = filters.nodeTypes.includes(type)
      ? filters.nodeTypes.filter((item) => item !== type)
      : [...filters.nodeTypes, type];
    onChange({ ...filters, nodeTypes });
  };

  const toggleRelationshipType = (type: string) => {
    const relationshipTypes = filters.relationshipTypes.includes(type)
      ? filters.relationshipTypes.filter((item) => item !== type)
      : [...filters.relationshipTypes, type];
    onChange({ ...filters, relationshipTypes });
  };

  return (
    <div className="rounded-md border border-border bg-white p-3 dark:bg-slate-950">
      <p className="text-sm font-semibold">Filters</p>
      <div className="mt-3 space-y-4">
        <div>
          <p className="text-xs font-medium uppercase text-slate-500 dark:text-slate-400">Node type</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {nodeTypes.map((type) => (
              <button
                key={type}
                onClick={() => toggleNodeType(type)}
                className={`rounded px-2 py-1 text-xs font-medium ${
                  filters.nodeTypes.includes(type)
                    ? "bg-primary text-white"
                    : "bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-300"
                }`}
              >
                {type === "FailureMode" ? "Failure Mode" : type}
              </button>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs font-medium uppercase text-slate-500 dark:text-slate-400">Relationship</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {relationshipTypes.map((type) => (
              <button
                key={type}
                onClick={() => toggleRelationshipType(type)}
                className={`rounded px-2 py-1 text-xs font-medium ${
                  filters.relationshipTypes.includes(type)
                    ? "bg-slate-950 text-white dark:bg-slate-100 dark:text-slate-950"
                    : "bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-300"
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs font-medium uppercase text-slate-500 dark:text-slate-400">Expansion depth</p>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {[1, 2].map((depth) => (
              <button
                key={depth}
                onClick={() => onChange({ ...filters, depth: depth as 1 | 2 })}
                className={`rounded-md border px-3 py-2 text-sm ${
                  filters.depth === depth
                    ? "border-primary bg-primary text-white"
                    : "border-border bg-white dark:bg-slate-950"
                }`}
              >
                {depth}-hop
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

