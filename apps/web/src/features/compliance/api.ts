import axios from "axios";

import { API_BASE_URL } from "@/lib/api-client";

import type { ComplianceDashboardData } from "./types";

const complianceClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
});

export async function getComplianceDashboard(): Promise<ComplianceDashboardData> {
  const response = await complianceClient.get<ComplianceDashboardData>("/compliance/dashboard");
  return response.data;
}
