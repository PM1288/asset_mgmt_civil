import { useMemo, useState } from "react";
import { getAuditLog } from "../api/admin";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import SectionCard from "../components/SectionCard";
import SkeletonCard from "../components/SkeletonCard";
import StatusBadge from "../components/StatusBadge";
import { useApiResource } from "../hooks/useApiResource";
import { formatDateTime } from "../utils/format";

export default function AdminAuditPage() {
  const audit = useApiResource(getAuditLog, []);
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const lower = query.trim().toLowerCase();
    return (audit.data || []).filter((item) => {
      if (!lower) {
        return true;
      }
      return (
        item.event_type.toLowerCase().includes(lower) ||
        (item.actor || "").toLowerCase().includes(lower) ||
        (item.detail_message || "").toLowerCase().includes(lower)
      );
    });
  }, [audit.data, query]);

  return (
    <div className="view-stack">
      <div className="page-title-row">
        <div>
          <p className="page-kicker">Support visibility</p>
          <h1>Activity history</h1>
          <p className="page-summary">Recent service, workflow, and support actions recorded by the platform.</p>
        </div>
      </div>

      <SectionCard title="Recent activity events" eyebrow="Recorded actions" icon="audit">
        <div className="filter-bar">
          <input placeholder="Filter by event, actor, or detail" value={query} onChange={(event) => setQuery(event.target.value)} />
        </div>
        {audit.loading ? (
          <SkeletonCard lines={6} />
        ) : audit.error ? (
          <ErrorState description={audit.error} />
        ) : !filtered.length ? (
          <EmptyState title="No audit events match the current filter" description="Broaden the search or refresh the audit view." />
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Event</th>
                <th>Outcome</th>
                <th>Actor</th>
                <th>Detail</th>
                <th>At</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr key={item.id}>
                  <td>{item.event_type}</td>
                  <td><StatusBadge status={item.outcome} /></td>
                  <td>{item.actor || "System"}</td>
                  <td>{item.detail_message || "-"}</td>
                  <td>{formatDateTime(item.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </SectionCard>
    </div>
  );
}
