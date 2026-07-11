import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  AlertCircle,
  Ban,
  Brain,
  CheckCircle2,
  Circle,
  Database,
  FileText,
  GitBranch,
  Loader2,
  RefreshCcw,
  ServerCog,
  Sparkles,
  Upload,
  UploadCloud,
  X,
} from "lucide-react";
import { ChangeEvent, DragEvent, useMemo, useRef, useState } from "react";

import { SectionCard } from "@/components/dashboard/SectionCard";
import { EmptyState } from "@/components/shared/EmptyState";
import { ErrorState } from "@/components/shared/ErrorState";
import { LoadingState } from "@/components/shared/LoadingState";
import { invalidateOperationalData, queryKeys } from "@/lib/query-keys";
import { cn } from "@/lib/utils";

import { fetchDocuments, getUploadErrorMessage, isCancelledUpload, uploadPdfDocuments } from "./api";
import type { DocumentSummary, DocumentUploadResult, UploadStage, UploadStatus } from "./types";

type QueueItem = {
  id: string;
  file: File;
  progress: number;
  stage: UploadStage;
  status: UploadStatus;
  result?: DocumentUploadResult;
  error?: string;
  controller?: AbortController;
  startedAt?: string;
  completedAt?: string;
};

type UploadMutationInput = {
  itemId: string;
  file: File;
  controller: AbortController;
};

const processingStages: Array<{ id: UploadStage; label: string; icon: typeof UploadCloud }> = [
  { id: "uploading", label: "Uploading", icon: UploadCloud },
  { id: "extracting", label: "Extracting Text", icon: FileText },
  { id: "ocr", label: "Running OCR", icon: Sparkles },
  { id: "chunking", label: "Chunking Document", icon: ServerCog },
  { id: "entities", label: "Extracting Entities", icon: Brain },
  { id: "graph", label: "Building Knowledge Graph", icon: GitBranch },
  { id: "embeddings", label: "Generating Embeddings", icon: Database },
  { id: "risk", label: "Risk Analysis", icon: Brain },
  { id: "digitalTwin", label: "Updating Digital Twin", icon: RefreshCcw },
  { id: "completed", label: "Completed", icon: CheckCircle2 },
];

const stageOrder = processingStages.map((stage) => stage.id);

export function DocumentUploadPage() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const stageTimersRef = useRef<Record<string, number>>({});
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [dropError, setDropError] = useState<string | null>(null);

  const activeUploads = useMemo(
    () => queue.filter((item) => item.status === "uploading" || item.status === "processing").length,
    [queue],
  );

  const documentsQuery = useQuery({
    queryKey: queryKeys.documents,
    queryFn: fetchDocuments,
    refetchInterval: activeUploads ? 5_000 : 30_000,
  });

  const uploadMutation = useMutation({
    mutationFn: ({ itemId, file, controller }: UploadMutationInput) => {
      return uploadPdfDocuments([file], controller.signal, (progress) => {
        updateQueueItem(itemId, {
          progress,
          status: progress >= 100 ? "processing" : "uploading",
          stage: progress >= 100 ? "extracting" : "uploading",
        });
      });
    },
    onSuccess: async (documents, { itemId }) => {
      stopStageTimer(itemId);
      const result = documents[0];
      const timestamp = new Date().toISOString();

      updateQueueItem(itemId, {
        status: "completed",
        stage: "completed",
        progress: 100,
        result,
        completedAt: timestamp,
        controller: undefined,
      });

      await invalidateOperationalData(queryClient);
    },
    onError: (error, { itemId }) => {
      stopStageTimer(itemId);
      const status = isCancelledUpload(error) ? "cancelled" : "failed";
      const timestamp = new Date().toISOString();

      updateQueueItem(itemId, {
        status,
        controller: undefined,
        error: getUploadErrorMessage(error),
        completedAt: timestamp,
      });

      void queryClient.invalidateQueries({ queryKey: queryKeys.documents });
    },
  });

  function updateQueueItem(itemId: string, patch: Partial<QueueItem>) {
    setQueue((current) => current.map((item) => (item.id === itemId ? { ...item, ...patch } : item)));
  }

  function stopStageTimer(itemId: string) {
    const timer = stageTimersRef.current[itemId];

    if (timer) {
      window.clearInterval(timer);
      delete stageTimersRef.current[itemId];
    }
  }

  function beginStageTimer(itemId: string) {
    stopStageTimer(itemId);

    stageTimersRef.current[itemId] = window.setInterval(() => {
      setQueue((current) =>
        current.map((item) => {
          if (item.id !== itemId || (item.status !== "uploading" && item.status !== "processing")) {
            return item;
          }

          const currentIndex = Math.max(0, stageOrder.indexOf(item.stage));
          const nextStage = stageOrder[Math.min(stageOrder.length - 2, currentIndex + 1)];

          return {
            ...item,
            status: item.progress >= 100 ? "processing" : item.status,
            stage: nextStage,
          };
        }),
      );
    }, 1_100);
  }

  function startUpload(itemId: string, file: File) {
    const controller = new AbortController();
    updateQueueItem(itemId, {
      controller,
      error: undefined,
      progress: 0,
      result: undefined,
      startedAt: new Date().toISOString(),
      status: "uploading",
      stage: "uploading",
    });
    beginStageTimer(itemId);
    uploadMutation.mutate({ itemId, file, controller });
  }

  function addFiles(files: File[]) {
    setDropError(null);

    const pdfs = files.filter(isPdfFile);
    const rejected = files.length - pdfs.length;

    if (rejected) {
      setDropError(`${rejected} file${rejected === 1 ? "" : "s"} skipped. PlantMind accepts PDF documents only.`);
    }

    if (!pdfs.length) {
      return;
    }

    const items = pdfs.map<QueueItem>((file) => ({
      id: crypto.randomUUID(),
      file,
      progress: 0,
      stage: "queued",
      status: "queued",
    }));

    setQueue((current) => [...items, ...current]);
    items.forEach((item) => startUpload(item.id, item.file));
  }

  function handleFileInput(event: ChangeEvent<HTMLInputElement>) {
    addFiles(Array.from(event.target.files ?? []));
    event.target.value = "";
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    addFiles(Array.from(event.dataTransfer.files));
  }

  function cancelUpload(item: QueueItem) {
    item.controller?.abort();
    stopStageTimer(item.id);
    updateQueueItem(item.id, {
      status: "cancelled",
      error: "Upload cancelled.",
      completedAt: new Date().toISOString(),
      controller: undefined,
    });
  }

  function retryUpload(item: QueueItem) {
    startUpload(item.id, item.file);
  }

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <header className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-medium text-primary">Document intelligence</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-normal">Industrial document upload</h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-600 dark:text-slate-300">
            Ingest PDF procedures, incident reports, inspection packs, and maintenance records into the PlantMind
            knowledge pipeline.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-2 text-center sm:flex">
          <HeaderMetric label="Queued" value={queue.filter((item) => item.status === "queued").length} />
          <HeaderMetric label="Active" value={activeUploads} />
          <HeaderMetric label="Completed" value={queue.filter((item) => item.status === "completed").length} />
        </div>
      </header>

      <section className="grid gap-5 xl:grid-cols-[1.25fr_0.75fr]">
        <SectionCard title="Upload documents" description="Multiple PDFs are processed through the live backend pipeline">
          <div
            onDragOver={(event) => {
              event.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={cn(
              "flex min-h-72 flex-col items-center justify-center rounded-md border border-dashed p-8 text-center transition",
              isDragging
                ? "border-primary bg-primary/5"
                : "border-border bg-slate-50 hover:border-primary/60 dark:bg-slate-900",
            )}
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-md bg-primary text-white shadow-sm">
              <UploadCloud className="h-6 w-6" />
            </div>
            <h2 className="mt-4 text-base font-semibold">Drop industrial PDFs here</h2>
            <p className="mt-2 max-w-md text-sm leading-6 text-slate-600 dark:text-slate-300">
              Upload one or more PDF files to extract text, build graph context, generate embeddings, and refresh related
              digital twins.
            </p>
            <div className="mt-5 flex flex-wrap items-center justify-center gap-2">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="inline-flex h-9 items-center gap-2 rounded-md bg-primary px-3 text-sm font-medium text-white shadow-sm"
              >
                <Upload className="h-4 w-4" />
                Browse files
              </button>
              <span className="text-xs text-slate-500 dark:text-slate-400">PDF only, multiple files supported</span>
            </div>
            <input ref={fileInputRef} type="file" accept="application/pdf,.pdf" multiple hidden onChange={handleFileInput} />
          </div>

          {dropError ? (
            <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950/30 dark:text-amber-200">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                {dropError}
              </div>
            </div>
          ) : null}
        </SectionCard>

        <SectionCard title="Recent uploads" description="Live ingestion outcomes from this session">
          <div className="mb-3 flex justify-end">
            <button
              type="button"
              onClick={() => void documentsQuery.refetch()}
              className="inline-flex h-8 items-center gap-2 rounded-md border border-border px-3 text-xs font-medium hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60 dark:hover:bg-slate-900"
              disabled={documentsQuery.isFetching}
            >
              <RefreshCcw className={cn("h-3.5 w-3.5", documentsQuery.isFetching && "animate-spin")} />
              Refresh
            </button>
          </div>
          {documentsQuery.isLoading ? (
            <LoadingState label="Loading uploaded documents" />
          ) : documentsQuery.isError ? (
            <ErrorState message="Uploaded documents could not be loaded. You can retry with refresh." />
          ) : documentsQuery.data?.length ? (

            <div className="max-h-[650px] overflow-y-auto pr-2 space-y-3">
              {documentsQuery.data.slice(0, 12).map((item) => (
                <HistoryRow key={item.document_id} item={item} />
                ))}
            </div>
          ) : (
            <EmptyState title="No uploads yet" description="Completed, failed, and cancelled uploads will appear here." />
          )}
        </SectionCard>
        
      </section>

      <SectionCard title="Upload queue" description="Track progress, processing stages, and backend ingestion results">
        {queue.length ? (
          <div className="space-y-4">
            {queue.map((item) => (
              <QueueCard key={item.id} item={item} onCancel={cancelUpload} onRetry={retryUpload} />
            ))}
          </div>
        ) : (
          <EmptyState title="Queue is empty" description="Drop PDF files or browse your workstation to start ingestion." />
        )}
      </SectionCard>
    </motion.div>
  );
}

function HeaderMetric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-border bg-white px-4 py-2 dark:bg-slate-950">
      <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
      <p className="text-lg font-semibold">{value}</p>
    </div>
  );
}

function QueueCard({
  item,
  onCancel,
  onRetry,
}: {
  item: QueueItem;
  onCancel: (item: QueueItem) => void;
  onRetry: (item: QueueItem) => void;
}) {
  const canCancel = item.status === "uploading" || item.status === "processing";
  const canRetry = item.status === "failed" || item.status === "cancelled";

  return (
    <article className="rounded-md border border-border bg-white p-4 shadow-sm dark:bg-slate-950">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 shrink-0 text-primary" />
            <h3 className="truncate text-sm font-semibold">{item.file.name}</h3>
            <StatusBadge status={item.status} />
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            {formatBytes(item.file.size)}
            {item.startedAt ? ` - Started ${formatTime(item.startedAt)}` : ""}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {canCancel ? (
            <button
              type="button"
              onClick={() => onCancel(item)}
              className="inline-flex h-8 items-center gap-2 rounded-md border border-border px-3 text-xs font-medium hover:bg-slate-50 dark:hover:bg-slate-900"
            >
              <Ban className="h-3.5 w-3.5" />
              Cancel
            </button>
          ) : null}
          {canRetry ? (
            <button
              type="button"
              onClick={() => onRetry(item)}
              className="inline-flex h-8 items-center gap-2 rounded-md bg-primary px-3 text-xs font-medium text-white"
            >
              <RefreshCcw className="h-3.5 w-3.5" />
              Retry
            </button>
          ) : null}
        </div>
      </div>

      <div className="mt-4">
        <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <span>{getStageLabel(item.stage)}</span>
          <span>{item.progress}%</span>
        </div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
          <motion.div
            className={cn("h-full rounded-full", item.status === "failed" ? "bg-red-500" : "bg-primary")}
            animate={{ width: `${item.progress}%` }}
            transition={{ duration: 0.25 }}
          />
        </div>
      </div>

      <ProcessingTimeline stage={item.stage} status={item.status} />

      {item.error ? (
        <div className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">
          <div className="flex items-center gap-2">
            <X className="h-4 w-4" />
            {item.error}
          </div>
        </div>
      ) : null}

      {item.result ? <UploadResultPanel result={item.result} /> : null}
    </article>
  );
}

function ProcessingTimeline({ stage, status }: { stage: UploadStage; status: UploadStatus }) {
  const currentIndex = status === "completed" ? stageOrder.length - 1 : Math.max(0, stageOrder.indexOf(stage));

  return (
    <div className="mt-5 grid gap-2 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-5">
      {processingStages.map((step, index) => {
        const Icon = step.icon;
        const isComplete = index < currentIndex || status === "completed";
        const isCurrent = index === currentIndex && (status === "uploading" || status === "processing");

        return (
          <div
            key={step.id}
            className={cn(
              "flex min-h-12 items-center gap-2 rounded-md border px-3 py-2 text-xs transition",
              isComplete && "border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950/30 dark:text-emerald-200",
              isCurrent && "border-primary bg-primary/5 text-primary",
              !isComplete && !isCurrent && "border-border bg-slate-50 text-slate-500 dark:bg-slate-900 dark:text-slate-400",
            )}
          >
            {isComplete ? (
              <CheckCircle2 className="h-4 w-4 shrink-0" />
            ) : isCurrent ? (
              <Loader2 className="h-4 w-4 shrink-0 animate-spin" />
            ) : (
              <Icon className="h-4 w-4 shrink-0" />
            )}
            <span className="truncate">{step.label}</span>
          </div>
        );
      })}
    </div>
  );
}

function UploadResultPanel({ result }: { result: DocumentUploadResult }) {
  const metrics = [
    { label: "Document ID", value: result.document_id },
    { label: "Chunks Created", value: result.chunks_created.toLocaleString() },
    { label: "Entities Found", value: result.entities_found.toLocaleString() },
    { label: "Graph Nodes", value: result.graph_nodes_created.toLocaleString() },
    { label: "Graph Edges", value: result.graph_edges_created.toLocaleString() },
  ];

  return (
    <div className="mt-4 grid gap-3 border-t border-border pt-4 sm:grid-cols-2 xl:grid-cols-5">
      {metrics.map((metric) => (
        <div key={metric.label} className="rounded-md border border-border bg-slate-50 p-3 dark:bg-slate-900">
          <p className="text-xs text-slate-500 dark:text-slate-400">{metric.label}</p>
          <p className="mt-1 truncate text-sm font-semibold">{metric.value}</p>
        </div>
      ))}
    </div>
  );
}

function HistoryRow({ item }: { item: DocumentSummary }) {
  return (
    <div className="rounded-md border border-border bg-slate-50 p-3 dark:bg-slate-900">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-sm font-medium">{item.filename}</p>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            {formatBytes(item.file_size_bytes)} - Uploaded {formatTime(item.upload_timestamp)}
          </p>
          <p className="mt-1 truncate text-xs text-slate-500 dark:text-slate-400">{item.document_id}</p>
          <div className="mt-3 grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
            <HistoryMetric label="Entities" value={item.extracted_entities.toLocaleString()} />
            <HistoryMetric label="Chunks" value={item.chunks_created.toLocaleString()} />
            <HistoryMetric label="Graph nodes" value={item.graph_nodes_created.toLocaleString()} />
            <HistoryMetric label="Duration" value={formatDuration(item.processing_duration_ms)} />
          </div>
          {item.error ? <p className="mt-2 text-xs text-red-600 dark:text-red-300">{item.error}</p> : null}
        </div>
        <StatusBadge status={normalizeDocumentStatus(item.status)} />
      </div>
    </div>
  );
}

function HistoryMetric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-slate-500 dark:text-slate-400">{label}</p>
      <p className="font-medium text-slate-900 dark:text-slate-100">{value}</p>
    </div>
  );
}

function StatusBadge({ status }: { status: UploadStatus }) {
  const styles: Record<UploadStatus, string> = {
    queued: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200",
    uploading: "bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-200",
    processing: "bg-primary/10 text-primary",
    completed: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-200",
    failed: "bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-200",
    cancelled: "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-200",
  };

  return (
    <span className={cn("inline-flex shrink-0 items-center gap-1 rounded px-2 py-1 text-xs font-medium", styles[status])}>
      {status === "completed" ? <CheckCircle2 className="h-3 w-3" /> : status === "failed" ? <AlertCircle className="h-3 w-3" /> : <Circle className="h-3 w-3" />}
      {status}
    </span>
  );
}

function getStageLabel(stage: UploadStage) {
  return processingStages.find((item) => item.id === stage)?.label ?? "Queued";
}

function isPdfFile(file: File) {
  return file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
}

function formatBytes(bytes: number) {
  if (!bytes) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** index;

  return `${value.toFixed(value >= 10 || index === 0 ? 0 : 1)} ${units[index]}`;
}

function formatTime(timestamp: string) {
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    month: "short",
    day: "numeric",
  }).format(new Date(timestamp));
}

function formatDuration(durationMs?: number | null) {
  if (durationMs == null) {
    return "Pending";
  }

  if (durationMs < 1000) {
    return `${durationMs} ms`;
  }

  return `${(durationMs / 1000).toFixed(1)} s`;
}

function normalizeDocumentStatus(status: string): UploadStatus {
  if (status === "completed" || status === "processed") {
    return "completed";
  }
  if (status === "failed") {
    return "failed";
  }
  return "processing";
}
