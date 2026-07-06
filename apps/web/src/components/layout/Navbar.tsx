import { Bell, Moon, PanelLeft, Sun } from "lucide-react";

import { SearchBar } from "@/components/shared/SearchBar";
import { useAppStore } from "@/stores/app-store";

export function Navbar() {
  const isDarkMode = useAppStore((state) => state.isDarkMode);
  const toggleDarkMode = useAppStore((state) => state.toggleDarkMode);

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-background/88 backdrop-blur">
      <div className="flex h-16 items-center gap-3 px-4 sm:px-6 lg:px-8">
        <button className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-border bg-white text-slate-600 dark:bg-slate-950 dark:text-slate-300 lg:hidden">
          <PanelLeft className="h-4 w-4" />
        </button>
        <SearchBar />
        <div className="ml-auto flex items-center gap-2">
          <button className="relative inline-flex h-9 w-9 items-center justify-center rounded-md border border-border bg-white text-slate-600 dark:bg-slate-950 dark:text-slate-300">
            <Bell className="h-4 w-4" />
            <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-destructive" />
          </button>
          <button
            onClick={toggleDarkMode}
            className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-border bg-white text-slate-600 dark:bg-slate-950 dark:text-slate-300"
            aria-label="Toggle dark mode"
          >
            {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
          <div className="hidden items-center gap-3 rounded-md border border-border bg-white px-3 py-1.5 dark:bg-slate-950 sm:flex">
            <div className="h-7 w-7 rounded-md bg-slate-900 text-center text-xs font-semibold leading-7 text-white dark:bg-slate-100 dark:text-slate-950">
              DS
            </div>
            <div className="text-xs">
              <p className="font-semibold">Ops Admin</p>
              <p className="text-slate-500 dark:text-slate-400">Plant A</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

