export type RiskLevel = "Low" | "Medium" | "High" | "Critical";

export type RiskSummary = {
  level: RiskLevel;
  score: number;
  explanation: string;
  trend: number[];
};

export type RiskAsset = {
  equipment_id: string;
  name?: string | null;
  risk_score: number;
  risk_level: RiskLevel;
  incident_count: number;
  failure_mode_count: number;
  criticality_score: number;
};

export type RiskFailureMode = {
  failure_mode: string;
  mentions: number;
  severity: RiskLevel;
  last_seen?: string | null;
};

export type RiskAlert = {
  id: string;
  asset_id?: string | null;
  title: string;
  severity: RiskLevel;
  timestamp: string;
  incident_id?: string | null;
};

export type RiskRecommendation = {
  id: string;
  title: string;
  rationale: string;
  priority: RiskLevel;
  asset_id?: string | null;
  copilot_query: string;
};

export type RiskTimelineEvent = {
  id: string;
  title: string;
  description: string;
  event_type: string;
  severity: RiskLevel;
  timestamp: string;
  asset_id?: string | null;
  incident_id?: string | null;
};

export type RiskHeatmapCell = {
  asset_id: string;
  asset_name?: string | null;
  failure_mode: string;
  score: number;
  level: RiskLevel;
};

export type RiskDashboardData = {
  overall_risk: RiskSummary;
  risk_score: number;
  high_risk_assets: RiskAsset[];
  recurring_failure_modes: RiskFailureMode[];
  alerts: RiskAlert[];
  recommendations: RiskRecommendation[];
  timeline: RiskTimelineEvent[];
  heatmap: RiskHeatmapCell[];
};
