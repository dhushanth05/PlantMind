import { useQuery } from "@tanstack/react-query";

import { getAlertsDashboard } from "./api";

export function useAlertsDashboard() {
  return useQuery({
    queryKey: ["alerts", "dashboard"],
    queryFn: getAlertsDashboard,
    refetchInterval: 30_000,
  });
}
