import { NavLink } from "react-router-dom";

import { navigationItems, secondaryNavigation } from "@/components/layout/navigation";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/stores/app-store";

export function Sidebar() {
  const setActiveModule = useAppStore((state) => state.setActiveModule);

  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-72 border-r border-border bg-white/92 backdrop-blur dark:bg-slate-950/92 lg:block">
      <div className="flex h-full flex-col">
        <div className="border-b border-border px-5 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary text-sm font-bold text-white">
              PM
            </div>
            <div>
              <p className="text-sm font-semibold">PlantMind</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">Industrial intelligence</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          {navigationItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => setActiveModule(item.label)}
              className={({ isActive }) =>
                cn(
                  "group flex h-10 items-center gap-3 rounded-md px-3 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-900 dark:hover:text-white",
                  isActive && "bg-slate-950 text-white hover:bg-slate-950 hover:text-white dark:bg-slate-100 dark:text-slate-950",
                )
              }
            >
              <item.icon className="h-4 w-4 shrink-0" />
              <span className="truncate">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-border p-3">
          {secondaryNavigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900"
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
          <div className="mt-3 rounded-md border border-border bg-slate-50 p-3 text-xs text-slate-600 dark:bg-slate-900 dark:text-slate-300">
            <p className="font-semibold text-slate-900 dark:text-white">Inference status</p>
            <p className="mt-1">Hybrid retrieval, graph expansion, and copilot services are online.</p>
          </div>
        </div>
      </div>
    </aside>
  );
}

