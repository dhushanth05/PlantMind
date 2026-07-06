import axios from "axios";

import { API_BASE_URL } from "@/lib/api-client";

import type { AssetDigitalTwin } from "./types";

const assetsClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
});

export async function getAssetDigitalTwin(assetId: string): Promise<AssetDigitalTwin> {
  const response = await assetsClient.get<AssetDigitalTwin>(`/assets/${encodeURIComponent(assetId)}/digital-twin`);
  return response.data;
}
