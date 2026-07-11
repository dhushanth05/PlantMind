import { Component, ErrorInfo, ReactNode } from "react";

import { ErrorState } from "./ErrorState";

type ErrorBoundaryState = {
  error: Error | null;
};

export class ErrorBoundary extends Component<{ children: ReactNode }, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("plantmind_unhandled_render_error", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <main className="min-h-screen bg-slate-50 p-6 text-slate-950 dark:bg-slate-950 dark:text-slate-50">
          <ErrorState message="PlantMind hit an unexpected interface error. Refresh the page or retry the action." />
        </main>
      );
    }

    return this.props.children;
  }
}
