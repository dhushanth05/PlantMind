export function LoadingState({ label = "Loading operational data" }: { label?: string }) {
  return (
    <div className="flex min-h-48 items-center justify-center rounded-md border border-border bg-white dark:bg-slate-950">
      <div className="flex items-center gap-3 text-sm text-slate-500 dark:text-slate-400">
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-primary" />
        {label}
      </div>
    </div>
  );
}

