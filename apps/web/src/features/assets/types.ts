export type GraphNode = {
  id: string;
  labels: string[];
  properties: Record<string, unknown>;
};

export type RiskLevel = "Low" | "Medium" | "High" | "Critical";

export type HealthScore = {
  score: number;
  status: string;
};

export type RiskAssessment = {
  level: RiskLevel;
  explanation: string;
  score: number;
};

export type TimelineEvent = {
  event_type: "Inspection" | "Maintenance" | "Incident" | "Repair" | "Recommendation";
  title: string;
  description: string;
  timestamp?: string | null;
  source?: string | null;
  metadata: Record<string, unknown>;
};

export type GraphSummary = {
  connected_nodes: number;
  connected_documents: number;
  connected_engineers: number;
  failure_modes: number;
  procedures: number;
};

export type DigitalTwinRecommendation = {
  title: string;
  rationale: string;
  priority: RiskLevel;
};

export type RelatedAsset = {
  asset_id: string;
  name?: string | null;
  relationship: string;
  reason: string;
};

export type AssetDigitalTwin = {
  asset: GraphNode;
  health_score: HealthScore;
  risk_level: RiskAssessment;
  maintenance_history: TimelineEvent[];
  incidents: GraphNode[];
  connected_documents: GraphNode[];
  procedures: GraphNode[];
  assigned_personnel: GraphNode[];
  failure_modes: GraphNode[];
  recommendations: DigitalTwinRecommendation[];
  graph_summary: GraphSummary;
  related_assets: RelatedAsset[];
  operational_timeline: TimelineEvent[];
};
