/**
 * Root application component with routing and context providers.
 *
 * Sets up React Router, TanStack Query, and the AuthContext provider.
 * All routes are defined here.
 *
 * @module App
 */

import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/contexts/AuthContext";
import { AppShell } from "@/components/AppShell";
import { HomePage } from "@/pages/HomePage";
import { DocsListPage } from "@/pages/DocsListPage";
import { DocViewPage } from "@/pages/DocViewPage";
import { AuthCallbackPage } from "@/pages/AuthCallbackPage";
import { NotificationsPage } from "@/pages/NotificationsPage";
import { ChangesListPage } from "@/pages/ChangesListPage";
import { ChangeDetailPage } from "@/pages/ChangeDetailPage";
import { ProposeChangePage } from "@/pages/ProposeChangePage";

/** Shared query client for TanStack Query. */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      retry: 1,
    },
  },
});

/** Root component that wires together providers, layout, and routes. */
export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<AppShell />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/docs" element={<DocsListPage />} />
              <Route path="/docs/:slug" element={<DocViewPage />} />
              <Route path="/changes" element={<ChangesListPage />} />
              <Route path="/changes/new" element={<ProposeChangePage />} />
              <Route path="/changes/:prNumber" element={<ChangeDetailPage />} />
              <Route path="/notifications" element={<NotificationsPage />} />
            </Route>
            <Route path="/auth/callback" element={<AuthCallbackPage />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
