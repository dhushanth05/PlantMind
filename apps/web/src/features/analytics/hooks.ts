import { useQuery } from "@tanstack/react-query";

import { getExecutiveAnalytics } from "./api";

export function useExecutiveAnalytics() {
  return useQuery({
    queryKey: ["analytics", "executive"],
    queryFn: getExecutiveAnalytics,
    refetchInterval: 60_000,
  });
}
