export function GraphLoading() {
  return (
    <div className="absolute inset-0 z-20 flex items-center justify-center bg-white/70 backdrop-blur-sm dark:bg-slate-950/70">
      <div className="rounded-md border border-border bg-white px-4 py-3 shadow-sm dark:bg-slate-950">
        <div className="flex items-center gap-3 text-sm text-slate-600 dark:text-slate-300">
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-primary" />
          Expanding graph context
        </div>
      </div>
    </div>
  );
}

