import {
  AlertTriangle,
  BarChart3,
  Bot,
  FileText,
  Gauge,
  GitBranch,
  LayoutDashboard,
  Settings,
  ShieldCheck,
  Wrench,
} from "lucide-react";

export const navigationItems = [
  { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { label: "Documents", path: "/documents", icon: FileText },
  { label: "AI Copilot", path: "/copilot", icon: Bot },
  { label: "Knowledge Graph", path: "/graph", icon: GitBranch },
  { label: "Assets", path: "/assets", icon: Wrench },
  { label: "Risk Intelligence", path: "/risk", icon: Gauge },
  { label: "Compliance", path: "/compliance", icon: ShieldCheck },
  { label: "Alerts", path: "/alerts", icon: AlertTriangle },
  { label: "Analytics", path: "/analytics", icon: BarChart3 },
  { label: "Settings", path: "/settings", icon: Settings },
];

export const secondaryNavigation = [{ label: "Operational Review", path: "/analytics", icon: BarChart3 }];
