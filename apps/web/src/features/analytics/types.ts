export type ExecutiveKpi = {
  label: string;
  value: string;
  change: string;
  tone: string;
};

export type SeriesPoint = {
  label: string;
  value: number;
};

export type DistributionItem = {
  label: string;
  value: number;
};

export type AnalyticsInsight = {
  title: string;
  summary: string;
  priority: string;
};

export type ExecutiveAnalyticsData = {
  kpis: ExecutiveKpi[];
  knowledge_growth: SeriesPoint[];
  incident_trends: SeriesPoint[];
  asset_health_distribution: DistributionItem[];
  failure_distribution: DistributionItem[];
  operational_insights: AnalyticsInsight[];
  ai_summary: string;
};
