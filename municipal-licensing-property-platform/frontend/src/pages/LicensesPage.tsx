import { useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { createLicense, listLicenses } from "../api/licenses";
import { listProperties } from "../api/properties";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import SectionCard from "../components/SectionCard";
import SkeletonCard from "../components/SkeletonCard";
import StatusBadge from "../components/StatusBadge";
import { useApiResource } from "../hooks/useApiResource";
import { compactNumber, formatDateTime, formatRelative } from "../utils/format";
import { getEstimatedExpiryAt, getReviewDueAt } from "../utils/license";

const PAGE_SIZE = 8;

const LICENSE_FIELD_LABELS: Record<string, string> = {
  application_number: "Application number",
  property_id: "Property",
  license_type: "Application type",
  applicant_name: "Applicant name",
  applicant_contact: "Applicant phone",
  notes: "Notes"
};

export default function LicensesPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const licenses = useApiResource(listLicenses, []);
  const properties = useApiResource(listProperties, []);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [form, setForm] = useState({
    application_number: "",
    property_id: searchParams.get("propertyId") || "",
    license_type: "trade",
    applicant_name: "",
    applicant_contact: "",
    notes: ""
  });

  const query = (searchParams.get("q") || "").trim().toLowerCase();
  const statusFilter = searchParams.get("status") || "";
  const typeFilter = searchParams.get("type") || "";
  const assigneeFilter = searchParams.get("assignee") || "";
  const wardFilter = searchParams.get("ward") || "";
  const dueFilter = searchParams.get("due") || "";
  const renewalFilter = searchParams.get("renewal") || "";
  const focusFilter = searchParams.get("focus") || "";
  const page = Number(searchParams.get("page") || "1");
  const createOpen = searchParams.get("create") === "1";

  const propertyMap = useMemo(
    () => new Map((properties.data || []).map((item) => [item.id, item])),
    [properties.data]
  );

  const filtered = useMemo(() => {
    const statuses = statusFilter ? statusFilter.split(",") : [];
    const items = licenses.data || [];
    return items.filter((item) => {
      const propertyRecord = propertyMap.get(item.property_id);
      const dueAt = getReviewDueAt(item);
      const expiryAt = getEstimatedExpiryAt(item);
      const matchesQuery =
        !query ||
        item.application_number.toLowerCase().includes(query) ||
        item.applicant_name.toLowerCase().includes(query) ||
        propertyRecord?.property_number.toLowerCase().includes(query);
      const matchesStatus = !statuses.length || statuses.includes(item.status);
      const matchesType = !typeFilter || item.license_type === typeFilter;
      const matchesAssignee =
        !assigneeFilter ||
        (assigneeFilter === "unassigned" ? !item.current_assignee : item.current_assignee === assigneeFilter);
      const matchesWard = !wardFilter || propertyRecord?.ward_code === wardFilter;
      const matchesDue =
        !dueFilter ||
        (dueFilter === "today" && dueAt && formatRelative(dueAt.toISOString()) === "due today") ||
        (dueFilter === "overdue" && dueAt && formatRelative(dueAt.toISOString()).includes("overdue"));
      const matchesRenewal =
        !renewalFilter ||
        (renewalFilter === "overdue" && expiryAt && formatRelative(expiryAt.toISOString()).includes("overdue")) ||
        (renewalFilter === "soon" && expiryAt && !formatRelative(expiryAt.toISOString()).includes("overdue"));
      const matchesFocus =
        !focusFilter ||
        (focusFilter === "exceptions" && ["rejected", "revoked"].includes(item.status)) ||
        (focusFilter === "inspection" && item.license_type === "building");

      return matchesQuery && matchesStatus && matchesType && matchesAssignee && matchesWard && matchesDue && matchesRenewal && matchesFocus;
    });
  }, [licenses.data, propertyMap, query, statusFilter, typeFilter, assigneeFilter, wardFilter, dueFilter, renewalFilter, focusFilter]);

  const paged = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const wards = Array.from(new Set((properties.data || []).map((item) => item.ward_code))).sort();

  function setParam(key: string, value: string | null) {
    const next = new URLSearchParams(searchParams);
    if (!value) {
      next.delete(key);
    } else {
      next.set(key, value);
    }
    if (key !== "page") {
      next.set("page", "1");
    }
    setSearchParams(next);
  }

  async function submit() {
    setSubmitting(true);
    setSubmitError(null);
    try {
      const created = await createLicense(form);
      await licenses.reload();
      navigate(`/licenses/${created.id}`);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Unable to create license");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="view-stack">
      <div className="page-title-row">
        <div>
          <p className="page-kicker">Application services</p>
          <h1>Licenses</h1>
          <p className="page-summary">Track new requests, approvals, renewals, and supporting records across the municipal application process.</p>
        </div>
        <div className="inline-actions">
          <span className="badge-outline">{compactNumber(filtered.length)} records</span>
          <button className="button button-primary" onClick={() => setParam("create", createOpen ? null : "1")}>
            {createOpen ? "Hide create form" : "New license"}
          </button>
        </div>
      </div>

      {createOpen ? (
        <SectionCard title="Create license application" eyebrow="Start a request" icon="license">
          <div className="form-grid">
            <label>
              <span>{LICENSE_FIELD_LABELS.property_id}</span>
              <select value={form.property_id} onChange={(event) => setForm({ ...form, property_id: event.target.value })}>
                <option value="">Select property</option>
                {(properties.data || []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.property_number} · Ward {item.ward_code}
                  </option>
                ))}
              </select>
            </label>
            {Object.entries(form)
              .filter(([key]) => key !== "property_id")
              .map(([key, value]) => (
                <label key={key}>
                  <span>{LICENSE_FIELD_LABELS[key] || key.replace(/_/g, " ")}</span>
                  <input value={value} onChange={(event) => setForm({ ...form, [key]: event.target.value })} />
                </label>
              ))}
          </div>
          {submitError ? <ErrorState description={submitError} /> : null}
          <div className="inline-actions">
            <button className="button button-primary" disabled={submitting} onClick={() => void submit()}>
              {submitting ? "Creating..." : "Create license"}
            </button>
          </div>
        </SectionCard>
      ) : null}

      <SectionCard title="Application queue" eyebrow="Browse and filter" icon="summary">
        <div className="filter-bar">
          <input placeholder="Search application, applicant, or property" value={query} onChange={(event) => setParam("q", event.target.value || null)} />
          <select value={statusFilter} onChange={(event) => setParam("status", event.target.value || null)}>
            <option value="">All statuses</option>
            <option value="draft">Draft</option>
            <option value="submitted">Submitted</option>
            <option value="under_review">Under review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="revoked">Revoked</option>
          </select>
          <select value={typeFilter} onChange={(event) => setParam("type", event.target.value || null)}>
            <option value="">All types</option>
            <option value="trade">Trade</option>
            <option value="health">Health</option>
            <option value="fire">Fire</option>
            <option value="building">Building</option>
          </select>
          <select value={wardFilter} onChange={(event) => setParam("ward", event.target.value || null)}>
            <option value="">All wards</option>
            {wards.map((ward) => (
              <option key={ward} value={ward}>
                Ward {ward}
              </option>
            ))}
          </select>
          <select value={dueFilter} onChange={(event) => setParam("due", event.target.value || null)}>
            <option value="">Any due state</option>
            <option value="today">Due today</option>
            <option value="overdue">Overdue</option>
          </select>
          <select value={renewalFilter} onChange={(event) => setParam("renewal", event.target.value || null)}>
            <option value="">Any renewal state</option>
            <option value="soon">Expiring soon</option>
            <option value="overdue">Renewal overdue</option>
          </select>
        </div>
        {licenses.loading || properties.loading ? (
          <SkeletonCard lines={6} />
        ) : licenses.error || properties.error ? (
          <ErrorState description={licenses.error || properties.error || "Unable to load licenses"} />
        ) : !paged.length ? (
          <EmptyState title="No licenses match the current filters" description="Try broadening the queue filters or create a new application." />
        ) : (
          <>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Application</th>
                  <th>Property</th>
                  <th>Status</th>
                  <th>Assignee</th>
                  <th>Due</th>
                  <th>Renewal</th>
                </tr>
              </thead>
              <tbody>
                {paged.map((item) => {
                  const propertyRecord = propertyMap.get(item.property_id);
                  const dueAt = getReviewDueAt(item);
                  const expiryAt = getEstimatedExpiryAt(item);
                  return (
                    <tr key={item.id} onClick={() => navigate(`/licenses/${item.id}`)} className="table-row-link">
                      <td>
                        <strong>{item.application_number}</strong>
                        <div className="muted-text">{item.applicant_name}</div>
                      </td>
                      <td>
                        {propertyRecord ? (
                          <>
                            <div>{propertyRecord.property_number}</div>
                            <div className="muted-text">Ward {propertyRecord.ward_code}</div>
                          </>
                        ) : (
                          item.property_id
                        )}
                      </td>
                      <td><StatusBadge status={item.status} /></td>
                      <td>{item.current_assignee || "Unassigned"}</td>
                      <td>{dueAt ? formatRelative(dueAt.toISOString()) : "Not applicable"}</td>
                      <td>{expiryAt ? formatRelative(expiryAt.toISOString()) : "Pending approval"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div className="pagination-row">
              <span>
                Showing {(page - 1) * PAGE_SIZE + 1}-{Math.min(page * PAGE_SIZE, filtered.length)} of {filtered.length}
              </span>
              <div className="inline-actions">
                <button className="button button-secondary" disabled={page <= 1} onClick={() => setParam("page", String(page - 1))}>
                  Previous
                </button>
                <button className="button button-secondary" disabled={page >= totalPages} onClick={() => setParam("page", String(page + 1))}>
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </SectionCard>
    </div>
  );
}
