import { API_BASE_URL } from "@/lib/api-client";

import type { ChatApiResponse } from "./types";

export async function sendChatMessage(sessionId: string, message: string): Promise<ChatApiResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ session_id: sessionId, message }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "PlantMind Copilot request failed");
  }

  return response.json() as Promise<ChatApiResponse>;
}

export async function streamChatMessage(
  sessionId: string,
  message: string,
  onToken: (token: string) => void,
): Promise<ChatApiResponse> {
  const response = await sendChatMessage(sessionId, message);
  const tokens = response.answer.split(/(\s+)/);

  for (const token of tokens) {
    await new Promise((resolve) => window.setTimeout(resolve, 18));
    onToken(token);
  }

  return response;
}

