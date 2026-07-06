export type ComplianceSeverity = "Low" | "Medium" | "High" | "Critical";

export type ComplianceOverview = {
  score: number;
  status: string;
  total_documents: number;
  mapped_regulations: number;
  open_gaps: number;
  inspections_due: number;
};

export type ComplianceItem = {
  id: string;
  title: string;
  asset_id?: string | null;
  severity: ComplianceSeverity;
  due_date?: string | null;
  source?: string | null;
};

export type RegulatoryMapping = {
  framework: string;
  mapped_documents: number;
  gaps: number;
  status: string;
};

export type ComplianceRecommendation = {
  id: string;
  title: string;
  rationale: string;
  priority: ComplianceSeverity;
  copilot_query: string;
};

export type ComplianceDashboardData = {
  overview: ComplianceOverview;
  missing_sops: ComplianceItem[];
  inspections_due: ComplianceItem[];
  compliance_gaps: ComplianceItem[];
  regulatory_mapping: RegulatoryMapping[];
  recommendations: ComplianceRecommendation[];
};
