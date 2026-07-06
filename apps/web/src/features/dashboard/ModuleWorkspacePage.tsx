import { motion } from "framer-motion";

import { SectionCard } from "@/components/dashboard/SectionCard";

const moduleCopy: Record<string, { title: string; description: string; metrics: string[] }> = {
  documents: {
    title: "Documents",
    description: "Upload, parse, extract, and review industrial knowledge sources.",
    metrics: ["Upload queue: 4", "Parsed today: 86", "OCR needed: 9"],
  },
  copilot: {
    title: "AI Copilot",
    description: "Ask evidence-grounded questions over documents, assets, incidents, and graph context.",
    metrics: ["Sessions: 42", "Avg confidence: 91%", "Citations: 318"],
  },
  graph: {
    title: "Knowledge Graph",
    description: "Explore industrial entities, causal relationships, procedures, and assets.",
    metrics: ["Nodes: 42.7k", "Edges: 118k", "Assets linked: 612"],
  },
  assets: {
    title: "Assets",
    description: "Review AI-generated digital twins and asset-specific operational context.",
    metrics: ["Twins: 612", "Critical: 18", "Updated today: 73"],
  },
  risk: {
    title: "Risk Intelligence",
    description: "Track risk drivers, repeated failures, and emerging operating patterns.",
    metrics: ["Risk score: 74", "High scenarios: 12", "Mitigations: 39"],
  },
  compliance: {
    title: "Compliance",
    description: "Map evidence, controls, and obligations across standards and procedures.",
    metrics: ["Controls: 284", "Evidence gaps: 11", "Audit packs: 6"],
  },
  alerts: {
    title: "Alerts",
    description: "Triage operational alerts, overdue reviews, and AI-detected risk signals.",
    metrics: ["Open: 27", "Critical: 3", "Acknowledged: 19"],
  },
  settings: {
    title: "Settings",
    description: "Manage plant workspaces, integrations, user access, and model configuration.",
    metrics: ["Users: 48", "Connectors: 5", "Policies: 14"],
  },
};

export function ModuleWorkspacePage({ moduleId }: { moduleId: string }) {
  const module = moduleCopy[moduleId] ?? moduleCopy.documents;

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <header>
        <p className="text-sm font-medium text-primary">PlantMind workspace</p>
        <h1 className="mt-1 text-2xl font-semibold">{module.title}</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-600 dark:text-slate-300">{module.description}</p>
      </header>
      <div className="grid gap-3 md:grid-cols-3">
        {module.metrics.map((metric) => (
          <div key={metric} className="rounded-md border border-border bg-white p-4 shadow-sm dark:bg-slate-950">
            <p className="text-sm font-semibold">{metric}</p>
          </div>
        ))}
      </div>
      <SectionCard title={`${module.title} work queue`} description="Prioritized operational items for this module">
        <div className="grid gap-3 lg:grid-cols-3">
          {["Review", "Investigate", "Approve"].map((item) => (
            <div key={item} className="rounded-md border border-border p-4">
              <p className="text-sm font-semibold">{item}</p>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                Current items are organized by severity, evidence freshness, and asset criticality.
              </p>
            </div>
          ))}
        </div>
      </SectionCard>
    </motion.div>
  );
}

