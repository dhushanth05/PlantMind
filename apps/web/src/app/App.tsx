import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { lazy, Suspense, useEffect } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "@/components/layout/AppLayout";
import { LoadingState } from "@/components/shared/LoadingState";
import { DashboardPage } from "@/features/dashboard/DashboardPage";
import { ModuleWorkspacePage } from "@/features/dashboard/ModuleWorkspacePage";
import { useAppStore } from "@/stores/app-store";

const ChatPage = lazy(() => import("@/features/copilot/ChatPage").then((module) => ({ default: module.ChatPage })));
const DocumentUploadPage = lazy(() =>
  import("@/features/documents/DocumentUploadPage").then((module) => ({ default: module.DocumentUploadPage })),
);
const GraphPage = lazy(() => import("@/features/graph/GraphPage").then((module) => ({ default: module.GraphPage })));
const AssetDigitalTwinPage = lazy(() =>
  import("@/features/assets/AssetDigitalTwinPage").then((module) => ({ default: module.AssetDigitalTwinPage })),
);
const RiskDashboardPage = lazy(() =>
  import("@/features/risk/RiskDashboardPage").then((module) => ({ default: module.RiskDashboardPage })),
);
const ComplianceCenterPage = lazy(() =>
  import("@/features/compliance/ComplianceCenterPage").then((module) => ({ default: module.ComplianceCenterPage })),
);
const AlertsCenterPage = lazy(() =>
  import("@/features/alerts/AlertsCenterPage").then((module) => ({ default: module.AlertsCenterPage })),
);
const ExecutiveAnalyticsPage = lazy(() =>
  import("@/features/analytics/ExecutiveAnalyticsPage").then((module) => ({ default: module.ExecutiveAnalyticsPage })),
);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 45_000,
      refetchOnWindowFocus: false,
    },
  },
});

export function App() {
  const isDarkMode = useAppStore((state) => state.isDarkMode);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDarkMode);
  }, [isDarkMode]);

  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route
            path="/documents"
            element={
              <Suspense fallback={<LoadingState label="Loading Document Upload" />}>
                <DocumentUploadPage />
              </Suspense>
            }
          />
          <Route
            path="/copilot"
            element={
              <Suspense fallback={<LoadingState label="Loading AI Copilot" />}>
                <ChatPage />
              </Suspense>
            }
          />
          <Route
            path="/graph"
            element={
              <Suspense fallback={<LoadingState label="Loading Knowledge Graph" />}>
                <GraphPage />
              </Suspense>
            }
          />
          <Route path="/assets" element={<ModuleWorkspacePage moduleId="assets" />} />
          <Route
            path="/assets/:assetId"
            element={
              <Suspense fallback={<LoadingState label="Loading Digital Twin" />}>
                <AssetDigitalTwinPage />
              </Suspense>
            }
          />
          <Route
            path="/risk"
            element={
              <Suspense fallback={<LoadingState label="Loading Risk Intelligence" />}>
                <RiskDashboardPage />
              </Suspense>
            }
          />
          <Route
            path="/compliance"
            element={
              <Suspense fallback={<LoadingState label="Loading Compliance Center" />}>
                <ComplianceCenterPage />
              </Suspense>
            }
          />
          <Route
            path="/alerts"
            element={
              <Suspense fallback={<LoadingState label="Loading Alerts Center" />}>
                <AlertsCenterPage />
              </Suspense>
            }
          />
          <Route
            path="/analytics"
            element={
              <Suspense fallback={<LoadingState label="Loading Executive Analytics" />}>
                <ExecutiveAnalyticsPage />
              </Suspense>
            }
          />
          <Route path="/settings" element={<ModuleWorkspacePage moduleId="settings" />} />
        </Route>
      </Routes>
    </QueryClientProvider>
  );
}
