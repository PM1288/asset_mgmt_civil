import { useState } from "react";
import { getDashboardHealthSummary } from "../api/dashboard";
import { getDiagnosticsPayload, runBackup, triggerCleanup, validateLatestBackup } from "../api/admin";
import ErrorState from "../components/ErrorState";
import SectionCard from "../components/SectionCard";
import SkeletonCard from "../components/SkeletonCard";
import StatusBadge from "../components/StatusBadge";
import { useApiResource } from "../hooks/useApiResource";

export default function AdminPage() {
  const diagnostics = useApiResource(getDiagnosticsPayload, []);
  const summary = useApiResource(getDashboardHealthSummary, []);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busyAction, setBusyAction] = useState<string | null>(null);

  async function run(label: string, action: () => Promise<Record<string, unknown>>) {
    setBusyAction(label);
    setActionError(null);
    setActionMessage(null);
    try {
      const result = await action();
      setActionMessage(JSON.stringify(result));
      await Promise.all([diagnostics.reload(), summary.reload()]);
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "Admin action failed");
    } finally {
      setBusyAction(null);
    }
  }

  return (
    <div className="view-stack">
      <div className="page-title-row">
        <div>
          <p className="page-kicker">Support and maintenance</p>
          <h1>Support tools</h1>
          <p className="page-summary">Review service readiness, storage headroom, and controlled maintenance tasks for authorised teams.</p>
        </div>
      </div>

      {actionError ? <ErrorState description={actionError} /> : null}
      {actionMessage ? <div className="info-banner">{actionMessage}</div> : null}

      <section className="detail-grid">
        <SectionCard title="Service readiness" eyebrow="Core systems" icon="status">
          {summary.loading || !summary.data ? (
            <SkeletonCard lines={5} />
          ) : summary.error ? (
            <ErrorState description={summary.error} />
          ) : (
            <div className="health-dependency-list">
              {summary.data.dependencies.map((item) => (
                <div key={item.key} className="health-signal-card">
                  <div className="health-signal-title">
                    <span>{item.label}</span>
                    <StatusBadge status={item.status} />
                  </div>
                  <p>{item.detail}</p>
                </div>
              ))}
            </div>
          )}
        </SectionCard>

        <SectionCard title="Maintenance actions" eyebrow="Controlled tools" icon="support">
          <div className="action-stack">
            <button className="button button-primary" disabled={busyAction === "backup"} onClick={() => void run("backup", runBackup)}>
              {busyAction === "backup" ? "Running backup..." : "Run backup"}
            </button>
            <button className="button button-secondary" disabled={busyAction === "validate"} onClick={() => void run("validate", validateLatestBackup)}>
              {busyAction === "validate" ? "Validating..." : "Validate latest backup"}
            </button>
            <button className="button button-secondary" disabled={busyAction === "cleanup"} onClick={() => void run("cleanup", triggerCleanup)}>
              {busyAction === "cleanup" ? "Cleaning up..." : "Run maintenance cleanup"}
            </button>
          </div>
        </SectionCard>
      </section>

      <SectionCard title="Storage and limits" eyebrow="Capacity" icon="summary">
        {diagnostics.loading || !diagnostics.data ? (
          <SkeletonCard lines={4} />
        ) : diagnostics.error ? (
          <ErrorState description={diagnostics.error} />
        ) : (
          <div className="summary-grid">
            <div>
              <span className="muted-text">Total storage</span>
              <strong>{diagnostics.data.disk.total_mb} MB</strong>
            </div>
            <div>
              <span className="muted-text">Used storage</span>
              <strong>{diagnostics.data.disk.used_mb} MB</strong>
            </div>
            <div>
              <span className="muted-text">Free storage</span>
              <strong>{diagnostics.data.disk.free_mb} MB</strong>
            </div>
            <div>
              <span className="muted-text">Disk pressure threshold</span>
              <strong>{diagnostics.data.limits.disk_pressure_threshold_percent}%</strong>
            </div>
          </div>
        )}
      </SectionCard>

      <SectionCard title="Advanced technical payload" eyebrow="Troubleshooting" icon="audit">
        {diagnostics.loading || !diagnostics.data ? (
          <SkeletonCard lines={4} />
        ) : diagnostics.error ? (
          <ErrorState description={diagnostics.error} />
        ) : (
          <details>
            <summary>Expand diagnostics JSON</summary>
            <pre className="code-box">{JSON.stringify(diagnostics.data, null, 2)}</pre>
          </details>
        )}
      </SectionCard>
    </div>
  );
}
