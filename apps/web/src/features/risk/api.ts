import axios from "axios";

import { API_BASE_URL } from "@/lib/api-client";

import type { RiskDashboardData } from "./types";

const riskClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
});

export async function getRiskDashboard(): Promise<RiskDashboardData> {
  const response = await riskClient.get<RiskDashboardData>("/risk/dashboard");
  return response.data;
}
