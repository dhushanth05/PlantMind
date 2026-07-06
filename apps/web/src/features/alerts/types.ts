export type AlertSeverity = "Low" | "Medium" | "High" | "Critical";
export type AlertStatus = "Open" | "Acknowledged" | "Resolved";

export type AlertRecord = {
  id: string;
  title: string;
  severity: AlertSeverity;
  status: AlertStatus;
  asset_id?: string | null;
  failure_mode?: string | null;
  timestamp: string;
  description?: string | null;
  incident_id?: string | null;
};

export type AlertSummary = {
  active: number;
  critical: number;
  high: number;
  resolved: number;
};

export type AlertsDashboardData = {
  summary: AlertSummary;
  active_alerts: AlertRecord[];
  alert_history: AlertRecord[];
};
