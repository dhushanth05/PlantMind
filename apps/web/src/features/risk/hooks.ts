import { useQuery } from "@tanstack/react-query";

import { getRiskDashboard } from "./api";

export function useRiskDashboard() {
  return useQuery({
    queryKey: ["risk", "dashboard"],
    queryFn: getRiskDashboard,
    refetchInterval: 30_000,
  });
}
