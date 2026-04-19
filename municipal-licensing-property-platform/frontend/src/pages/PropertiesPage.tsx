import { useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { createProperty, listProperties } from "../api/properties";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import SectionCard from "../components/SectionCard";
import SkeletonCard from "../components/SkeletonCard";
import StatusBadge from "../components/StatusBadge";
import { useApiResource } from "../hooks/useApiResource";
import { formatDateTime } from "../utils/format";

const PAGE_SIZE = 8;

const PROPERTY_FIELD_LABELS: Record<string, string> = {
  property_number: "Property number",
  ward_code: "Ward",
  address_line_1: "Street address",
  city: "City",
  district: "District",
  state: "State",
  status: "Record status",
  use_type: "Property use",
  owner_name: "Owner name",
  owner_contact: "Owner phone",
  remarks: "Notes"
};

export default function PropertiesPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const properties = useApiResource(listProperties, []);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [form, setForm] = useState({
    property_number: "",
    ward_code: "",
    address_line_1: "",
    city: "Pune",
    district: "Pune",
    state: "Maharashtra",
    status: "active",
    use_type: "commercial",
    owner_name: "",
    owner_contact: "",
    remarks: ""
  });

  const createOpen = searchParams.get("create") === "1";
  const query = (searchParams.get("q") || "").trim().toLowerCase();
  const ward = searchParams.get("ward") || "";
  const status = searchParams.get("status") || "";
  const sort = searchParams.get("sort") || "updated";
  const page = Number(searchParams.get("page") || "1");

  const filtered = useMemo(() => {
    const items = properties.data || [];
    return items
      .filter((item) => {
        const matchesQuery =
          !query ||
          item.property_number.toLowerCase().includes(query) ||
          item.address_line_1.toLowerCase().includes(query) ||
          item.owner_name.toLowerCase().includes(query);
        const matchesWard = !ward || item.ward_code === ward;
        const matchesStatus = !status || item.status === status;
        return matchesQuery && matchesWard && matchesStatus;
      })
      .sort((left, right) => {
        if (sort === "property_number") {
          return left.property_number.localeCompare(right.property_number);
        }
        return new Date(right.updated_at).getTime() - new Date(left.updated_at).getTime();
      });
  }, [properties.data, query, ward, status, sort]);

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
      const created = await createProperty(form);
      setForm({
        property_number: "",
        ward_code: "",
        address_line_1: "",
        city: "Pune",
        district: "Pune",
        state: "Maharashtra",
        status: "active",
        use_type: "commercial",
        owner_name: "",
        owner_contact: "",
        remarks: ""
      });
      await properties.reload();
      navigate(`/properties/${created.id}`);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Unable to create property");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="view-stack">
      <div className="page-title-row">
        <div>
          <p className="page-kicker">Property services</p>
          <h1>Properties</h1>
          <p className="page-summary">Search, update, and create property records that support licence and renewal services.</p>
        </div>
        <button className="button button-primary" onClick={() => setParam("create", createOpen ? null : "1")}>
          {createOpen ? "Hide create form" : "New property"}
        </button>
      </div>

      {createOpen ? (
        <SectionCard title="Create property" eyebrow="Start a new record" icon="property">
          <div className="form-grid">
            {Object.entries(form).map(([key, value]) => (
              <label key={key}>
                <span>{PROPERTY_FIELD_LABELS[key] || key.replace(/_/g, " ")}</span>
                <input
                  value={value}
                  onChange={(event) => setForm({ ...form, [key]: event.target.value })}
                />
              </label>
            ))}
          </div>
          {submitError ? <ErrorState description={submitError} /> : null}
          <div className="inline-actions">
            <button className="button button-primary" disabled={submitting} onClick={() => void submit()}>
              {submitting ? "Creating..." : "Create property"}
            </button>
          </div>
        </SectionCard>
      ) : null}

      <SectionCard title="Property list" eyebrow="Browse records" icon="summary">
        <div className="filter-bar">
          <input
            placeholder="Search by number, address, or owner"
            value={query}
            onChange={(event) => setParam("q", event.target.value || null)}
          />
          <select value={ward} onChange={(event) => setParam("ward", event.target.value || null)}>
            <option value="">All wards</option>
            {wards.map((item) => (
              <option key={item} value={item}>
                Ward {item}
              </option>
            ))}
          </select>
          <select value={status} onChange={(event) => setParam("status", event.target.value || null)}>
            <option value="">All statuses</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
          <select value={sort} onChange={(event) => setParam("sort", event.target.value)}>
            <option value="updated">Recently updated</option>
            <option value="property_number">Property number</option>
          </select>
        </div>
        {properties.loading ? (
          <SkeletonCard lines={6} />
        ) : properties.error ? (
          <ErrorState description={properties.error} action={<button className="button button-secondary" onClick={() => void properties.reload()}>Retry</button>} />
        ) : !paged.length ? (
          <EmptyState title="No properties match the current filters" description="Adjust the search filters or create a new property record." />
        ) : (
          <>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Property</th>
                  <th>Ward</th>
                  <th>Use</th>
                  <th>Status</th>
                  <th>Owner</th>
                  <th>Updated</th>
                </tr>
              </thead>
              <tbody>
                {paged.map((item) => (
                  <tr key={item.id} onClick={() => navigate(`/properties/${item.id}`)} className="table-row-link">
                    <td>
                      <strong>{item.property_number}</strong>
                      <div className="muted-text">{item.address_line_1}</div>
                    </td>
                    <td>{item.ward_code}</td>
                    <td>{item.use_type}</td>
                    <td><StatusBadge status={item.status} /></td>
                    <td>{item.owner_name}</td>
                    <td>{formatDateTime(item.updated_at)}</td>
                  </tr>
                ))}
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
