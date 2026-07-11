import { useQuery } from "@tanstack/react-query";

import { fetchDashboardData } from "@/features/dashboard/api/dashboard";

export function useDashboardData() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: ({ signal }) => fetchDashboardData(signal),
    refetchInterval: 30_000,
  });
}
