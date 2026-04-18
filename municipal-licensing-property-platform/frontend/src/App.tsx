import { useState } from "react";
import { getCurrentSubject } from "./api/health";
import DashboardPage from "./pages/DashboardPage";
import PropertiesPage from "./pages/PropertiesPage";
import LicensesPage from "./pages/LicensesPage";
import HealthPage from "./pages/HealthPage";
import AdminPage from "./pages/AdminPage";
import { useAsync } from "./hooks/useAsync";
import "./styles/app.css";

type Tab = "dashboard" | "properties" | "licenses" | "health" | "admin";

export default function App() {
  const [tab, setTab] = useState<Tab>("dashboard");
  const subject = useAsync(getCurrentSubject, []);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1>Municipal Suite</h1>
        <p>{subject.data?.username || "Authenticating…"}</p>
        {(["dashboard", "properties", "licenses", "health", "admin"] as Tab[]).map((item) => (
          <button
            key={item}
            className={tab === item ? "active" : ""}
            onClick={() => setTab(item)}
          >
            {item.toUpperCase()}
          </button>
        ))}
      </aside>
      <main className="content">
        {tab === "dashboard" && <DashboardPage subject={subject.data} />}
        {tab === "properties" && <PropertiesPage />}
        {tab === "licenses" && <LicensesPage />}
        {tab === "health" && <HealthPage />}
        {tab === "admin" && <AdminPage />}
      </main>
    </div>
  );
}
