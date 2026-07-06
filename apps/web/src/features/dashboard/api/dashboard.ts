import axios from "axios";

import { API_BASE_URL } from "@/lib/api-client";

export type DashboardStat = {
  label: string;
  value: string;
  delta: string;
  tone: "neutral" | "good" | "warning" | "danger";
  trend: number[];
};

export type ActivityItem = {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  type: "document" | "graph" | "asset" | "alert";
};

export type AlertItem = {
  id: string;
  asset: string;
  title: string;
  severity: "Low" | "Medium" | "High" | "Critical";
  timestamp: string;
};

export type RecentUpload = {
  id: string;
  document_name: string;
  status: string;
  timestamp: string;
  document_id?: string | null;
};

export type CriticalEquipment = {
  equipment_id: string;
  name?: string | null;
  degree?: number | null;
  incident_count?: number | null;
  failure_mode_count?: number | null;
  criticality_score?: number | null;
};

export type FrequentFailureMode = {
  failure_mode: string;
  mentions: number;
};

export type DashboardData = {
  stats: DashboardStat[];
  activities: ActivityItem[];
  alerts: AlertItem[];
  recent_uploads: RecentUpload[];
  critical_equipment: CriticalEquipment[];
  frequent_failure_modes: FrequentFailureMode[];
  graph: {
    nodes: number;
    relationships: number;
    clusters: { label: string; value: number }[];
  };
  risk: {
    score: number;
    level: "Low" | "Medium" | "High" | "Critical";
    explanation: string;
  };
  quick_actions: { label: string; description: string; path: string }[];
};

const dashboardClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
});

export async function fetchDashboardData(): Promise<DashboardData> {
  const response = await dashboardClient.get<DashboardData>("/dashboard");
  return response.data;
}
