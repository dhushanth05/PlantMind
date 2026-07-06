import { useQuery } from "@tanstack/react-query";

import { getComplianceDashboard } from "./api";

export function useComplianceDashboard() {
  return useQuery({
    queryKey: ["compliance", "dashboard"],
    queryFn: getComplianceDashboard,
    refetchInterval: 60_000,
  });
}
