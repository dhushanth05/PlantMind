import axios from "axios";

import { API_BASE_URL } from "@/lib/api-client";

export type FactoryResetDeletedCounts = {
  documents: number;
  chunks: number;
  embeddings: number;
  graphNodes: number;
  graphRelationships: number;
  cacheKeys: number;
  uploadedFiles: number;
};

export type FactoryResetResponse = {
  success: boolean;
  deleted: FactoryResetDeletedCounts;
};

const settingsClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120_000,
});

export async function factoryReset() {
  const response = await settingsClient.delete<FactoryResetResponse>("/admin/factory-reset");
  return response.data;
}
