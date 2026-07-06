import axios from "axios";

import { API_BASE_URL } from "@/lib/api-client";

import type { AlertsDashboardData } from "./types";

const alertsClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
});

export async function getAlertsDashboard(): Promise<AlertsDashboardData> {
  const response = await alertsClient.get<AlertsDashboardData>("/alerts/dashboard");
  return response.data;
}
