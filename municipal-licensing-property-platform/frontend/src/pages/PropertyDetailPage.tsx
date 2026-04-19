import { ChangeEvent, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { downloadDocument, uploadPropertyDocument } from "../api/documents";
import { listLicenses } from "../api/licenses";
import { getProperty, listPropertyDocuments, updateProperty } from "../api/properties";
import { listWorkflowHistory } from "../api/workflows";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import SectionCard from "../components/SectionCard";
import SkeletonCard from "../components/SkeletonCard";
import StatusBadge from "../components/StatusBadge";
import { useApiResource } from "../hooks/useApiResource";
import { formatDateTime } from "../utils/format";

export default function PropertyDetailPage() {
  const { propertyId = "" } = useParams();
  const property = useApiResource(() => getProperty(propertyId), [propertyId]);
  const licenses = useApiResource(listLicenses, []);
  const documents = useApiResource(() => listPropertyDocuments(propertyId), [propertyId]);
  const workflow = useApiResource(() => listWorkflowHistory("property", propertyId), [propertyId]);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [form, setForm] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!property.data) {
      return;
    }
    setForm({
      ward_code: property.data.ward_code,
      address_line_1: property.data.address_line_1,
      city: property.data.city,
      district: property.data.district,
      state: property.data.state,
      status: property.data.status,
      use_type: property.data.use_type,
      owner_name: property.data.owner_name,
      owner_contact: property.data.owner_contact || "",
      remarks: property.data.remarks || ""
    });
  }, [property.data]);

  const relatedLicenses = useMemo(
    () => (licenses.data || []).filter((item) => item.property_id === propertyId),
    [licenses.data, propertyId]
  );

  async function saveChanges() {
    setSaving(true);
    setSaveError(null);
    try {
      await updateProperty(propertyId, form);
      await Promise.all([property.reload(), workflow.reload()]);
    } catch (error) {
      setSaveError(error instanceof Error ? error.message : "Unable to save property");
    } finally {
      setSaving(false);
    }
  }

  async function onFileSelected(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    setUploading(true);
    try {
      await uploadPropertyDocument(propertyId, file);
      await documents.reload();
    } catch (error) {
      setSaveError(error instanceof Error ? error.message : "Unable to upload document");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  if (property.loading || !property.data) {
    return <SkeletonCard lines={8} />;
  }

  if (property.error) {
    return <ErrorState description={property.error} />;
  }

  return (
    <div className="view-stack">
      <div className="page-title-row">
        <div>
          <p className="page-kicker">Property details</p>
          <h1>{property.data.property_number}</h1>
          <p className="page-summary">{property.data.address_line_1}</p>
        </div>
        <div className="inline-actions">
          <Link className="button button-secondary" to={`/licenses?create=1&propertyId=${property.data.id}`}>
            Create linked license
          </Link>
        </div>
      </div>

      <section className="detail-grid">
        <SectionCard title="Property summary" eyebrow="Overview" icon="property">
          <div className="summary-grid">
            <div>
              <span className="muted-text">Ward</span>
              <strong>{property.data.ward_code}</strong>
            </div>
            <div>
              <span className="muted-text">Use type</span>
              <strong>{property.data.use_type}</strong>
            </div>
            <div>
              <span className="muted-text">Status</span>
              <StatusBadge status={property.data.status} />
            </div>
            <div>
              <span className="muted-text">Last updated</span>
              <strong>{formatDateTime(property.data.updated_at)}</strong>
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Edit property" eyebrow="Record updates" icon="activity">
          <div className="form-grid">
            {Object.entries(form).map(([key, value]) => (
              <label key={key}>
                <span>{key.replace(/_/g, " ")}</span>
                <input value={value} onChange={(event) => setForm({ ...form, [key]: event.target.value })} />
              </label>
            ))}
          </div>
          {saveError ? <ErrorState description={saveError} /> : null}
          <div className="inline-actions">
            <button className="button button-primary" disabled={saving} onClick={() => void saveChanges()}>
              {saving ? "Saving..." : "Save changes"}
            </button>
          </div>
        </SectionCard>
      </section>

      <section className="detail-grid">
        <SectionCard title="Related applications" eyebrow="Connected requests" icon="license">
          {!relatedLicenses.length ? (
            <EmptyState title="No licenses linked to this property" description="Create a license to start the property workflow timeline." />
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Application</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Applicant</th>
                </tr>
              </thead>
              <tbody>
                {relatedLicenses.map((item) => (
                  <tr key={item.id}>
                    <td><Link to={`/licenses/${item.id}`}>{item.application_number}</Link></td>
                    <td>{item.license_type}</td>
                    <td><StatusBadge status={item.status} /></td>
                    <td>{item.applicant_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </SectionCard>

        <SectionCard
          title="Documents"
          eyebrow="Supporting files"
          icon="documents"
          action={
            <label className="button button-secondary">
              {uploading ? "Uploading..." : "Upload document"}
              <input className="visually-hidden" type="file" onChange={onFileSelected} />
            </label>
          }
        >
          {documents.loading ? (
            <SkeletonCard lines={4} />
          ) : documents.error ? (
            <ErrorState description={documents.error} />
          ) : !documents.data?.length ? (
            <EmptyState title="No property documents" description="Upload survey notes, approvals, or evidence files to support linked licenses." />
          ) : (
            <ul className="activity-list">
              {documents.data.map((item) => (
                <li key={item.id}>
                  <button className="text-button" onClick={() => void downloadDocument(item.id, item.original_filename)}>
                    {item.original_filename}
                  </button>
                  <div className="activity-meta">
                    <span>{item.media_type}</span>
                    <span>{formatDateTime(item.created_at)}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </SectionCard>
      </section>

      <SectionCard title="Activity timeline" eyebrow="Recent changes" icon="activity">
        {workflow.loading ? (
          <SkeletonCard lines={4} />
        ) : workflow.error ? (
          <ErrorState description={workflow.error} />
        ) : !workflow.data?.length ? (
          <EmptyState title="No property workflow events yet" description="Property lifecycle activity will appear here after edits and linked actions." />
        ) : (
          <ul className="timeline-list">
            {workflow.data.map((item) => (
              <li key={item.id}>
                <div>
                  <strong>{item.action.replace(/_/g, " ")}</strong>
                  <p>{item.comments || "Property record change logged."}</p>
                </div>
                <span>{formatDateTime(item.created_at)}</span>
              </li>
            ))}
          </ul>
        )}
      </SectionCard>
    </div>
  );
}
