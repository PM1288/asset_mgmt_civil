import { BrowserRouter, Navigate, Outlet, Route, Routes } from "react-router-dom";
import AppShell from "./components/AppShell";
import AccessDenied from "./components/AccessDenied";
import ErrorState from "./components/ErrorState";
import SkeletonCard from "./components/SkeletonCard";
import { AppProvider, useAppContext } from "./context/AppContext";
import { getCurrentSubject } from "./api/health";
import { useApiResource } from "./hooks/useApiResource";
import AdminAuditPage from "./pages/AdminAuditPage";
import AdminPage from "./pages/AdminPage";
import DashboardPage from "./pages/DashboardPage";
import HealthPage from "./pages/HealthPage";
import LicenseDetailPage from "./pages/LicenseDetailPage";
import LicensesPage from "./pages/LicensesPage";
import NotFoundPage from "./pages/NotFoundPage";
import PropertyDetailPage from "./pages/PropertyDetailPage";
import PropertiesPage from "./pages/PropertiesPage";
import "./styles/app.css";

function RequireRoles({ roles }: { roles: Array<Parameters<ReturnType<typeof useAppContext>["hasRole"]>[0]> }) {
  const { hasRole } = useAppContext();
  return hasRole(...roles) ? <Outlet /> : <AccessDenied />;
}

function BootstrapScreen() {
  return (
    <div className="bootstrap-screen">
      <div className="bootstrap-card">
        <p className="app-sidebar-kicker">City services</p>
        <h1>Preparing your civic services portal</h1>
        <div className="bootstrap-grid">
          <SkeletonCard lines={4} />
          <SkeletonCard lines={4} />
          <SkeletonCard lines={4} />
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const subject = useApiResource(getCurrentSubject, []);

  if (subject.loading || !subject.data) {
    return <BootstrapScreen />;
  }

  if (subject.error) {
    return (
      <div className="bootstrap-screen">
        <div className="bootstrap-card">
          <ErrorState
            title="Unable to start the portal"
            description={subject.error}
            action={
              <button className="button button-primary" onClick={() => void subject.reload()}>
                Retry
              </button>
            }
          />
        </div>
      </div>
    );
  }

  return (
    <AppProvider subject={subject.data}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/" element={<Navigate replace to="/dashboard" />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/properties" element={<PropertiesPage />} />
            <Route path="/properties/:propertyId" element={<PropertyDetailPage />} />
            <Route path="/licenses" element={<LicensesPage />} />
            <Route path="/licenses/:licenseId" element={<LicenseDetailPage />} />
            <Route path="/health" element={<HealthPage />} />
            <Route element={<RequireRoles roles={["municipal-admin", "operator", "auditor"]} />}>
              <Route path="/admin/diagnostics" element={<AdminPage />} />
              <Route path="/admin/audit" element={<AdminAuditPage />} />
            </Route>
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}
