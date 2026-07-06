import axios from "axios";

import { API_BASE_URL } from "@/lib/api-client";

import type { ExecutiveAnalyticsData } from "./types";

const analyticsClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
});

export async function getExecutiveAnalytics(): Promise<ExecutiveAnalyticsData> {
  const response = await analyticsClient.get<ExecutiveAnalyticsData>("/analytics/dashboard");
  return response.data;
}
