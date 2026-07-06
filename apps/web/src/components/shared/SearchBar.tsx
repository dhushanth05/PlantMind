import { Search } from "lucide-react";

export function SearchBar() {
  return (
    <label className="relative flex w-full max-w-2xl items-center">
      <Search className="pointer-events-none absolute left-3 h-4 w-4 text-slate-400" />
      <input
        className="h-10 w-full rounded-md border border-border bg-white pl-9 pr-3 text-sm text-slate-900 shadow-sm transition placeholder:text-slate-400 dark:bg-slate-950 dark:text-white"
        placeholder="Search assets, procedures, incidents, documents"
      />
    </label>
  );
}

