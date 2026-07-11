import type { QueryClient } from "@tanstack/react-query";

export const queryKeys = {
  alerts: ["alerts"] as const,
  analytics: ["analytics"] as const,
  assets: ["assets"] as const,
  compliance: ["compliance"] as const,
  copilotContext: ["copilot-context"] as const,
  dashboard: ["dashboard"] as const,
  documents: ["documents"] as const,
  graph: ["graph"] as const,
  risk: ["risk"] as const,
  search: ["search"] as const,
};

export async function invalidateOperationalData(queryClient: QueryClient) {
  await Promise.all([
    queryClient.invalidateQueries({ queryKey: queryKeys.documents }),
    queryClient.invalidateQueries({ queryKey: queryKeys.dashboard }),
    queryClient.invalidateQueries({ queryKey: queryKeys.graph }),
    queryClient.invalidateQueries({ queryKey: queryKeys.assets }),
    queryClient.invalidateQueries({ queryKey: queryKeys.search }),
    queryClient.invalidateQueries({ queryKey: queryKeys.copilotContext }),
    queryClient.invalidateQueries({ queryKey: queryKeys.analytics }),
    queryClient.invalidateQueries({ queryKey: queryKeys.risk }),
    queryClient.invalidateQueries({ queryKey: queryKeys.compliance }),
    queryClient.invalidateQueries({ queryKey: queryKeys.alerts }),
  ]);
}
