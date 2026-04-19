import { Link } from "react-router-dom";
import { getDashboardCompliance, getDashboardHealthSummary, getDashboardQueues, getDashboardRecentActivity, getDashboardSummary } from "../api/dashboard";
import AppIcon from "../components/AppIcon";
import QueueCard from "../components/QueueCard";
import SectionCard from "../components/SectionCard";
import SkeletonCard from "../components/SkeletonCard";
import StatCard from "../components/StatCard";
import StatusBadge from "../components/StatusBadge";
import { useAppContext } from "../context/AppContext";
import { useApiResource } from "../hooks/useApiResource";
import { compactNumber, formatDateTime, formatRelative } from "../utils/format";

const KPI_ROUTES: Record<string, string> = {
  total_properties: "/properties",
  active_licenses: "/licenses?status=approved",
  licenses_pending_review: "/licenses?status=submitted,under_review",
  approvals_due_today: "/licenses?due=today",
  overdue_renewals: "/licenses?renewal=overdue",
  unresolved_exceptions: "/licenses?focus=exceptions"
};

const QUEUE_ROUTES: Record<string, string> = {
  submitted_unassigned: "/licenses?status=submitted&assignee=unassigned",
  under_review: "/licenses?status=under_review",
  waiting_for_inspection: "/licenses?focus=inspection",
  waiting_for_applicant_response: "/licenses?status=rejected",
  due_today: "/licenses?due=today",
  overdue: "/licenses?due=overdue"
};

export default function DashboardPage() {
  const { hasRole } = useAppContext();
  const summary = useApiResource(getDashboardSummary, []);
  const queues = useApiResource(getDashboardQueues, []);
  const recent = useApiResource(getDashboardRecentActivity, []);
  const compliance = useApiResource(getDashboardCompliance, []);
  const health = useApiResource(getDashboardHealthSummary, []);

  const reloadAll = async () => {
    await Promise.all([summary.reload(), queues.reload(), recent.reload(), compliance.reload(), health.reload()]);
  };

  return (
    <div className="view-stack">
      <div className="page-title-row">
        <div>
          <p className="page-kicker">Welcome back</p>
          <h1>Dashboard</h1>
          <p className="page-summary">
            Review service demand, municipal applications, supporting documents, and delivery assurance from one official portal.
          </p>
        </div>
        <button className="button button-secondary" onClick={() => void reloadAll()}>
          Refresh dashboard
        </button>
      </div>

      <section className="page-grid page-grid-main">
        <SectionCard title="Public service commitments" eyebrow="Why departments can trust this service" icon="trust">
          <div className="trust-grid">
            <article className="trust-card">
              <span className="trust-card-icon">
                <AppIcon name="citizen" size={18} />
              </span>
              <div>
                <h4>Citizen-facing by default</h4>
                <p>Clear service language, guided screens, and mobile-ready layouts help staff serve applicants without exposing internal tooling.</p>
              </div>
            </article>
            <article className="trust-card">
              <span className="trust-card-icon">
                <AppIcon name="audit" size={18} />
              </span>
              <div>
                <h4>Auditable decisions</h4>
                <p>Every property update, application movement, and privileged action can be traced through activity history and workflow records.</p>
              </div>
            </article>
            <article className="trust-card">
              <span className="trust-card-icon">
                <AppIcon name="support" size={18} />
              </span>
              <div>
                <h4>Self-hosted control</h4>
                <p>Identity, storage, backups, and diagnostics remain under municipal infrastructure control, ready for Cloudflare Tunnel publishing.</p>
              </div>
            </article>
            <article className="trust-card">
              <span className="trust-card-icon">
                <AppIcon name="status" size={18} />
              </span>
              <div>
                <h4>Operational assurance</h4>
                <p>Live dependency checks, backup validation, and service summaries provide an immediate picture of readiness before public rollout.</p>
              </div>
            </article>
          </div>
        </SectionCard>

        <SectionCard title="Executive briefing" eyebrow="For commissioners and IAS review" icon="briefing">
          {summary.loading || !summary.data || health.loading || !health.data ? (
            <SkeletonCard lines={5} />
          ) : (
            <div className="briefing-card">
              <div className="briefing-status-row">
                <StatusBadge status={health.data.overall_status} label={`Platform ${health.data.overall_status}`} />
                <span className="briefing-highlight">{summary.data.approvals_due_today} approvals need attention today</span>
              </div>
              <ul className="briefing-list">
                <li>
                  <strong>{summary.data.licenses_pending_review}</strong> applications are in the active review pipeline and can be opened directly from queue widgets below.
                </li>
                <li>
                  <strong>{summary.data.overdue_renewals}</strong> renewals are already overdue, while expiring permits are surfaced in the compliance panel for preventive follow-up.
                </li>
                <li>
                  <strong>{summary.data.unresolved_exceptions}</strong> exceptions still require documentary or supervisory intervention before closure.
                </li>
              </ul>
              <div className="briefing-actions">
                <Link className="button button-primary" to="/licenses?due=today">
                  Open today&apos;s actions
                </Link>
                <Link className="button button-secondary" to="/health">
                  Review service assurance
                </Link>
              </div>
            </div>
          )}
        </SectionCard>
      </section>

      <section className="stats-grid">
        {summary.loading || !summary.data
          ? Array.from({ length: 6 }).map((_, index) => <SkeletonCard key={index} lines={2} />)
          : [
              ["total_properties", "Total properties", summary.data.total_properties, "Property registry"],
              ["active_licenses", "Active licenses", summary.data.active_licenses, "Currently approved"],
              ["licenses_pending_review", "Pending review", summary.data.licenses_pending_review, "Submitted or under review"],
              ["approvals_due_today", "Approvals due today", summary.data.approvals_due_today, "Needs same-day action"],
              ["overdue_renewals", "Overdue renewals", summary.data.overdue_renewals, "Past estimated expiry"],
              ["unresolved_exceptions", "Unresolved exceptions", summary.data.unresolved_exceptions, "Rejected, revoked, or missing evidence"]
            ].map(([key, title, value, helper]) => (
              <StatCard
                key={key}
                title={title}
                value={compactNumber(Number(value))}
                helper={String(helper)}
                icon={
                  key === "total_properties"
                    ? "property"
                    : key === "active_licenses"
                      ? "license"
                      : key === "licenses_pending_review"
                        ? "pending"
                        : key === "approvals_due_today"
                          ? "calendar"
                          : "warning"
                }
                to={KPI_ROUTES[String(key)]}
              />
            ))}
      </section>

      <section className="page-grid page-grid-main">
        <SectionCard title="Applications waiting for attention" eyebrow="Priority work" icon="summary">
          <div className="queue-grid">
            {queues.loading || !queues.data
              ? Array.from({ length: 6 }).map((_, index) => <SkeletonCard key={index} lines={2} />)
              : queues.data.items.map((item) => (
                  <QueueCard key={item.key} item={item} to={QUEUE_ROUTES[item.key] || "/licenses"} />
                ))}
          </div>
        </SectionCard>

        <SectionCard title="Popular actions" eyebrow="Get started" icon="activity">
          <div className="action-stack">
            <Link className="button button-primary" to="/properties?create=1">
              Add a property
            </Link>
            <Link className="button button-primary" to="/licenses?create=1">
              Start an application
            </Link>
            <Link className="button button-secondary" to="/licenses?status=submitted,under_review">
              Review applications
            </Link>
            <Link className="button button-secondary" to="/licenses?renewal=soon">
              View renewals
            </Link>
            {hasRole("municipal-admin", "operator", "auditor") ? (
              <Link className="button button-secondary" to="/admin/diagnostics">
                Open support tools
              </Link>
            ) : null}
          </div>
        </SectionCard>
      </section>

      <section className="page-grid">
        <SectionCard title="Recent updates" eyebrow="Latest changes" icon="activity">
          {recent.loading || !recent.data ? (
            <SkeletonCard lines={5} />
          ) : (
            <div className="activity-columns">
              <div>
                <h4>Recently updated</h4>
                <ul className="activity-list">
                  {recent.data.records.map((item) => (
                    <li key={`${item.entity_type}-${item.id}`}>
                      <Link to={item.route}>{item.title}</Link>
                      <p>{item.subtitle}</p>
                      <div className="activity-meta">
                        <StatusBadge status={item.status} />
                        <span>{formatDateTime(item.occurred_at)}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4>Application steps</h4>
                <ul className="activity-list">
                  {recent.data.workflow_transitions.map((item) => (
                    <li key={item.id}>
                      <Link to={item.route}>{item.action.replace(/_/g, " ")}</Link>
                      <p>
                        {item.from_state || "new"} to {item.to_state || "updated"} by {item.actor_subject}
                      </p>
                      <div className="activity-meta">
                        {item.to_state ? <StatusBadge status={item.to_state} /> : null}
                        <span>{formatDateTime(item.occurred_at)}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </SectionCard>

        <SectionCard title="Renewals and compliance" eyebrow="Time-sensitive items" icon="calendar">
          {compliance.loading || !compliance.data ? (
            <SkeletonCard lines={6} />
          ) : (
            <div className="compliance-stack">
              <div>
                <h4>Expiring soon</h4>
                <ul className="simple-list">
                  {compliance.data.upcoming_renewals.map((item) => (
                    <li key={item.id}>
                      <Link to={item.route}>{item.application_number}</Link>
                      <span>{formatRelative(item.estimated_expiry_at)}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4>Recently rejected</h4>
                <ul className="simple-list">
                  {compliance.data.recently_rejected.map((item) => (
                    <li key={item.id}>
                      <Link to={item.route}>{item.application_number}</Link>
                      <StatusBadge status={item.status} />
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4>Revoked items</h4>
                <ul className="simple-list">
                  {compliance.data.revoked_items.map((item) => (
                    <li key={item.id}>
                      <Link to={item.route}>{item.application_number}</Link>
                      <StatusBadge status={item.status} />
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </SectionCard>
      </section>

      <section className="page-grid">
        <SectionCard title="Documents and attachments" eyebrow="Supporting files" icon="documents">
          {recent.loading || !recent.data ? (
            <SkeletonCard lines={5} />
          ) : (
            <div className="activity-columns">
              <div>
                <h4>Latest uploads</h4>
                <ul className="activity-list">
                  {recent.data.latest_uploads.map((item) => (
                    <li key={item.id}>
                      <Link to={item.route}>{item.original_filename}</Link>
                      <p>{item.media_type}</p>
                      <div className="activity-meta">
                        <span>{item.uploaded_by}</span>
                        <span>{formatDateTime(item.occurred_at)}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4>Missing supporting files</h4>
                <ul className="activity-list">
                  {recent.data.missing_evidence.map((item) => (
                    <li key={item.license_id}>
                      <Link to={item.route}>{item.application_number}</Link>
                      <p>{item.detail}</p>
                      <div className="activity-meta">
                        <StatusBadge status={item.status} />
                        <span>{item.license_type}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </SectionCard>

        <SectionCard title="Service status" eyebrow="Platform snapshot" icon="status">
          {health.loading || !health.data ? (
            <SkeletonCard lines={4} />
          ) : (
            <div className="health-overview">
              <div className={`health-summary-card health-summary-${health.data.overall_status}`}>
                <h4>Overall status</h4>
                <StatusBadge status={health.data.overall_status} label={health.data.overall_status} />
                <p>Essential services, storage pressure, and integrations are summarised in plain language.</p>
              </div>
              <div className="health-dependency-list">
                {health.data.dependencies.map((item) => (
                  <div key={item.key} className="health-signal-card">
                    <div className="health-signal-title">
                      <span>{item.label}</span>
                      <StatusBadge status={item.status} />
                    </div>
                    <p>{item.detail}</p>
                  </div>
                ))}
                {health.data.signals.map((item) => (
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
      </section>
    </div>
  );
}
