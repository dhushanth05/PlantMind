import { useMutation, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, Loader2, ShieldAlert, Trash2, X } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { SectionCard } from "@/components/dashboard/SectionCard";
import { useToast } from "@/components/shared/toast-context";
import { invalidateOperationalData } from "@/lib/query-keys";
import { cn } from "@/lib/utils";

import { factoryReset } from "./api";

const CONFIRMATION_TEXT = "FACTORY RESET";

const deletedData = [
  "Uploaded PDF documents",
  "Extracted document chunks",
  "Embeddings / vector search data",
  "Knowledge Graph nodes & relationships",
  "Asset intelligence generated from uploaded documents",
  "Cached AI/chat/search data",
  "Temporary processing artifacts",
];

export function SettingsPage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [confirmation, setConfirmation] = useState("");
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { notify } = useToast();

  const mutation = useMutation({
    mutationFn: factoryReset,
    onSuccess: async (response) => {
      await queryClient.invalidateQueries();
      await invalidateOperationalData(queryClient);
      queryClient.removeQueries();
      notify(`Factory reset complete. Removed ${formatDeletedSummary(response.deleted)}.`, "success");
      setIsDialogOpen(false);
      setConfirmation("");
      navigate("/dashboard", { replace: true });
    },
    onError: () => {
      notify("Factory reset failed. Runtime data was not fully cleared.", "error");
    },
  });

  const canSubmit = confirmation === CONFIRMATION_TEXT && !mutation.isPending;

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (canSubmit) {
      mutation.mutate();
    }
  };

  return (
    <div className="space-y-5">
      <header>
        <p className="text-sm font-medium text-primary">PlantMind workspace</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-normal">Settings</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-600 dark:text-slate-300">
          Manage plant workspaces, integrations, user access, and model configuration.
        </p>
      </header>

      <div className="grid gap-3 md:grid-cols-3">
        {["Users: 48", "Connectors: 5", "Policies: 14"].map((metric) => (
          <div key={metric} className="rounded-md border border-border bg-white p-4 shadow-sm dark:bg-slate-950">
            <p className="text-sm font-semibold">{metric}</p>
          </div>
        ))}
      </div>

      <SectionCard title="Settings work queue" description="Prioritized operational items for this module">
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

      <DangerZone onFactoryReset={() => setIsDialogOpen(true)} isPending={mutation.isPending} />

      {isDialogOpen ? (
        <FactoryResetDialog
          confirmation={confirmation}
          isPending={mutation.isPending}
          canSubmit={canSubmit}
          onChange={setConfirmation}
          onClose={() => {
            if (!mutation.isPending) {
              setIsDialogOpen(false);
              setConfirmation("");
            }
          }}
          onSubmit={handleSubmit}
        />
      ) : null}
    </div>
  );
}

function DangerZone({ onFactoryReset, isPending }: { onFactoryReset: () => void; isPending: boolean }) {
  return (
    <section className="overflow-hidden rounded-md border border-red-300 bg-white shadow-sm dark:border-red-900 dark:bg-slate-950">
      <header className="border-b border-red-200 px-4 py-3 dark:border-red-900">
        <div className="flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-red-600 dark:text-red-300" />
          <h2 className="text-sm font-semibold text-red-700 dark:text-red-200">Danger Zone</h2>
        </div>
      </header>
      <div className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="max-w-2xl">
          <p className="text-sm font-semibold">Factory reset runtime data</p>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
            Permanently remove uploaded documents, generated graph data, AI caches, and temporary processing artifacts while preserving code,
            configuration, authentication, and project structure.
          </p>
        </div>
        <button
          type="button"
          onClick={onFactoryReset}
          disabled={isPending}
          className="inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-md border border-red-700 bg-red-600 px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
          Factory Reset
        </button>
      </div>
    </section>
  );
}

type FactoryResetDialogProps = {
  confirmation: string;
  isPending: boolean;
  canSubmit: boolean;
  onChange: (value: string) => void;
  onClose: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

function FactoryResetDialog({ confirmation, isPending, canSubmit, onChange, onClose, onSubmit }: FactoryResetDialogProps) {
  const pendingLabel = useMemo(
    () => (isPending ? "Clearing documents, graph data, embeddings, caches, and processing artifacts..." : null),
    [isPending],
  );

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-950/60 p-4">
      <form
        onSubmit={onSubmit}
        className="w-full max-w-2xl overflow-hidden rounded-md border border-red-300 bg-white shadow-2xl dark:border-red-900 dark:bg-slate-950"
      >
        <header className="flex items-start justify-between gap-4 border-b border-red-200 bg-red-50 px-4 py-3 dark:border-red-900 dark:bg-red-950/30">
          <div className="flex gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-red-600 dark:text-red-300" />
            <div>
              <h2 className="text-base font-semibold text-red-800 dark:text-red-100">Confirm Factory Reset</h2>
              <p className="mt-1 text-sm text-red-700 dark:text-red-200">This action permanently deletes runtime data.</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isPending}
            className="rounded p-1 text-red-700 hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-60 dark:text-red-200 dark:hover:bg-red-950"
            aria-label="Close factory reset confirmation"
          >
            <X className="h-4 w-4" />
          </button>
        </header>

        <div className="space-y-4 p-4">
          <p className="text-sm text-slate-700 dark:text-slate-200">Factory Reset will permanently delete:</p>
          <ul className="grid gap-2 text-sm text-slate-700 dark:text-slate-200 sm:grid-cols-2">
            {deletedData.map((item) => (
              <li key={item} className="flex gap-2">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-red-500" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
          <p className="rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200">
            Source code, Git history, Docker files, package files, requirements files, authentication/users, configuration, and environment files
            are preserved.
          </p>
          <label className="block text-sm font-medium" htmlFor="factory-reset-confirmation">
            Type <span className="font-semibold text-red-700 dark:text-red-200">{CONFIRMATION_TEXT}</span> to continue
          </label>
          <input
            id="factory-reset-confirmation"
            value={confirmation}
            onChange={(event) => onChange(event.target.value)}
            disabled={isPending}
            className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm shadow-sm disabled:cursor-not-allowed disabled:opacity-70 dark:bg-slate-950"
            autoComplete="off"
          />
          {pendingLabel ? (
            <div className="flex items-center gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-200">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>{pendingLabel}</span>
            </div>
          ) : null}
        </div>

        <footer className="flex flex-col-reverse gap-2 border-t border-border px-4 py-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={onClose}
            disabled={isPending}
            className="inline-flex h-10 items-center justify-center rounded-md border border-border px-4 text-sm font-semibold hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-70 dark:hover:bg-slate-900"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={!canSubmit}
            className={cn(
              "inline-flex h-10 items-center justify-center gap-2 rounded-md border border-red-700 bg-red-600 px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-60",
            )}
          >
            {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
            Permanently Factory Reset
          </button>
        </footer>
      </form>
    </div>
  );
}

function formatDeletedSummary(deleted: { uploadedFiles: number; documents: number; graphNodes: number; cacheKeys: number }) {
  return `${deleted.uploadedFiles} files, ${deleted.documents} documents, ${deleted.graphNodes} graph nodes, ${deleted.cacheKeys} cache keys`;
}
