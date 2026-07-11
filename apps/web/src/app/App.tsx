import { QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { lazy, Suspense, useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "@/components/layout/AppLayout";
import { ErrorBoundary } from "@/components/shared/ErrorBoundary";
import { LoadingState } from "@/components/shared/LoadingState";
import { OfflineBanner } from "@/components/shared/OfflineBanner";
import { ToastProvider } from "@/components/shared/Toast";
import { useToast } from "@/components/shared/toast-context";
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
const SettingsPage = lazy(() =>
  import("@/features/settings/SettingsPage").then((module) => ({ default: module.SettingsPage })),
);

export function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <PlantMindApp />
      </ToastProvider>
    </ErrorBoundary>
  );
}

function PlantMindApp() {
  const isDarkMode = useAppStore((state) => state.isDarkMode);
  const { notify } = useToast();
  const [queryClient] = useState(() => new QueryClient({
    queryCache: new QueryCache({
      onError: () => {
        notify("PlantMind could not refresh one of the live data views.", "error");
      },
    }),
    defaultOptions: {
      queries: {
        staleTime: 45_000,
        refetchOnReconnect: true,
        refetchOnWindowFocus: false,
        retry: 2,
      },
      mutations: {
        retry: 1,
      },
    },
  }));

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDarkMode);
  }, [isDarkMode]);

  return (
    <QueryClientProvider client={queryClient}>
      <OfflineBanner />
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
          <Route
            path="/settings"
            element={
              <Suspense fallback={<LoadingState label="Loading Settings" />}>
                <SettingsPage />
              </Suspense>
            }
          />
        </Route>
      </Routes>
    </QueryClientProvider>
  );
}
