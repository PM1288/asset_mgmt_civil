import { getDashboardHealthSummary } from "../api/dashboard";
import { getReadyHealth } from "../api/health";
import ErrorState from "../components/ErrorState";
import SectionCard from "../components/SectionCard";
import SkeletonCard from "../components/SkeletonCard";
import StatusBadge from "../components/StatusBadge";
import { useApiResource } from "../hooks/useApiResource";

export default function HealthPage() {
  const summary = useApiResource(getDashboardHealthSummary, []);
  const raw = useApiResource(getReadyHealth, []);

  return (
    <div className="view-stack">
      <div className="page-title-row">
        <div>
          <p className="page-kicker">Transparent status</p>
          <h1>Service status</h1>
          <p className="page-summary">Check whether property, application, identity, and document services are operating normally.</p>
        </div>
        <button className="button button-secondary" onClick={() => void Promise.all([summary.reload(), raw.reload()])}>
          Refresh service status
        </button>
      </div>

      <SectionCard title="Service overview" eyebrow="At a glance" icon="status">
        {summary.loading || !summary.data ? (
          <SkeletonCard lines={6} />
        ) : summary.error ? (
          <ErrorState description={summary.error} />
        ) : (
          <div className="health-overview">
            <div className={`health-summary-card health-summary-${summary.data.overall_status}`}>
              <h4>Overall</h4>
              <StatusBadge status={summary.data.overall_status} label={summary.data.overall_status} />
            </div>
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
              {summary.data.signals.map((item) => (
                <div key={item.key} className="health-signal-card">
                  <div className="health-signal-title">
                    <span>{item.label}</span>
                    <StatusBadge status={item.status} />
                  </div>
                  <p>{item.value}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </SectionCard>

      <SectionCard title="Advanced technical details" eyebrow="For support teams" icon="support">
        {raw.loading || !raw.data ? (
          <SkeletonCard lines={4} />
        ) : raw.error ? (
          <ErrorState description={raw.error} />
        ) : (
          <details>
            <summary>Expand raw readiness JSON</summary>
            <pre className="code-box">{JSON.stringify(raw.data, null, 2)}</pre>
          </details>
        )}
      </SectionCard>
    </div>
  );
}
