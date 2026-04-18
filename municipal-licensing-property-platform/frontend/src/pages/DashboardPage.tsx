import type { Subject } from "../types";
import Layout from "../components/Layout";

export default function DashboardPage({ subject }: { subject?: Subject | null }) {
  return (
    <Layout title="Dashboard">
      <div className="dashboard-grid">
        <div className="metric-card">
          <strong>User</strong>
          <div>{subject?.username || "Loading…"}</div>
        </div>
        <div className="metric-card">
          <strong>Roles</strong>
          <div>{subject?.roles?.join(", ") || "Loading…"}</div>
        </div>
        <div className="metric-card">
          <strong>Deployment Model</strong>
          <div>On-premises / Docker / Windows host</div>
        </div>
        <div className="metric-card">
          <strong>Auth</strong>
          <div>Keycloak + TOTP + optional LDAP federation</div>
        </div>
      </div>
    </Layout>
  );
}
