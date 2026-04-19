import { ChangeEvent, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { downloadDocument, uploadLicenseDocument } from "../api/documents";
import { getLicense, listLicenseDocuments, transitionLicense } from "../api/licenses";
import { getProperty } from "../api/properties";
import { listWorkflowHistory } from "../api/workflows";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import SectionCard from "../components/SectionCard";
import SkeletonCard from "../components/SkeletonCard";
import StatusBadge from "../components/StatusBadge";
import { useApiResource } from "../hooks/useApiResource";
import { formatDateTime, formatRelative } from "../utils/format";
import { getEstimatedExpiryAt, getReviewDueAt } from "../utils/license";

const ACTIONS_BY_STATUS: Record<string, Array<"submit" | "review" | "approve" | "reject" | "revoke">> = {
  draft: ["submit"],
  submitted: ["review"],
  under_review: ["approve", "reject"],
  approved: ["revoke"]
};

export default function LicenseDetailPage() {
  const { licenseId = "" } = useParams();
  const license = useApiResource(() => getLicense(licenseId), [licenseId]);
  const property = useApiResource(
    () => (license.data ? getProperty(license.data.property_id) : Promise.reject(new Error("Property not loaded"))),
    [license.data?.property_id]
  );
  const documents = useApiResource(() => listLicenseDocuments(licenseId), [licenseId]);
  const workflow = useApiResource(() => listWorkflowHistory("license", licenseId), [licenseId]);
  const [actionState, setActionState] = useState({ comments: "", assignee: "" });
  const [submitting, setSubmitting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const reviewDue = useMemo(() => (license.data ? getReviewDueAt(license.data) : null), [license.data]);
  const renewalDue = useMemo(() => (license.data ? getEstimatedExpiryAt(license.data) : null), [license.data]);

  async function runAction(action: "submit" | "review" | "approve" | "reject" | "revoke") {
    setSubmitting(action);
    setError(null);
    try {
      await transitionLicense(licenseId, action, {
        comments: actionState.comments || undefined,
        assignee: actionState.assignee || undefined
      });
      setActionState({ comments: "", assignee: "" });
      await Promise.all([license.reload(), workflow.reload()]);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to update license");
    } finally {
      setSubmitting(null);
    }
  }

  async function onFileSelected(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    try {
      await uploadLicenseDocument(licenseId, file);
      await documents.reload();
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to upload document");
    } finally {
      event.target.value = "";
    }
  }

  if (license.loading || !license.data) {
    return <SkeletonCard lines={8} />;
  }

  if (license.error) {
    return <ErrorState description={license.error} />;
  }

  const availableActions = ACTIONS_BY_STATUS[license.data.status] || [];

  return (
    <div className="view-stack">
      <div className="page-title-row">
        <div>
          <p className="page-kicker">Application details</p>
          <h1>{license.data.application_number}</h1>
          <p className="page-summary">
            {license.data.license_type} application for{" "}
            {property.data ? <Link to={`/properties/${property.data.id}`}>{property.data.property_number}</Link> : license.data.property_id}
          </p>
        </div>
      </div>

      <section className="detail-grid">
        <SectionCard title="Application summary" eyebrow="Overview" icon="license">
          <div className="summary-grid">
            <div>
              <span className="muted-text">Status</span>
              <StatusBadge status={license.data.status} />
            </div>
            <div>
              <span className="muted-text">Applicant</span>
              <strong>{license.data.applicant_name}</strong>
            </div>
            <div>
              <span className="muted-text">Current assignee</span>
              <strong>{license.data.current_assignee || "Unassigned"}</strong>
            </div>
            <div>
              <span className="muted-text">Review due</span>
              <strong>{reviewDue ? formatRelative(reviewDue.toISOString()) : "Not applicable"}</strong>
            </div>
            <div>
              <span className="muted-text">Estimated renewal</span>
              <strong>{renewalDue ? formatRelative(renewalDue.toISOString()) : "Pending approval"}</strong>
            </div>
            <div>
              <span className="muted-text">Last updated</span>
              <strong>{formatDateTime(license.data.updated_at)}</strong>
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Application actions" eyebrow="Next steps" icon="activity">
          {error ? <ErrorState description={error} /> : null}
          <div className="form-grid">
            <label>
              <span>Comments</span>
              <input
                value={actionState.comments}
                onChange={(event) => setActionState({ ...actionState, comments: event.target.value })}
              />
            </label>
            <label>
              <span>Assignee</span>
              <input
                value={actionState.assignee}
                onChange={(event) => setActionState({ ...actionState, assignee: event.target.value })}
                placeholder="Only used for review assignment"
              />
            </label>
          </div>
          <div className="inline-actions">
            {availableActions.map((action) => (
              <button
                key={action}
                className="button button-primary"
                disabled={submitting === action}
                onClick={() => void runAction(action)}
              >
                {submitting === action ? "Working..." : action.replace(/_/g, " ")}
              </button>
            ))}
          </div>
        </SectionCard>
      </section>

      <section className="detail-grid">
        <SectionCard
          title="Documents"
          eyebrow="Supporting files"
          icon="documents"
          action={
            <label className="button button-secondary">
              Upload document
              <input className="visually-hidden" type="file" onChange={onFileSelected} />
            </label>
          }
        >
          {documents.loading ? (
            <SkeletonCard lines={4} />
          ) : documents.error ? (
            <ErrorState description={documents.error} />
          ) : !documents.data?.length ? (
            <EmptyState title="No license documents uploaded" description="Attach supporting evidence and inspection notes to unlock downstream review actions." />
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

        <SectionCard title="Activity timeline" eyebrow="Recorded steps" icon="audit">
          {workflow.loading ? (
            <SkeletonCard lines={4} />
          ) : workflow.error ? (
            <ErrorState description={workflow.error} />
          ) : !workflow.data?.length ? (
            <EmptyState title="No workflow history yet" description="Status transitions and review notes will appear here." />
          ) : (
            <ul className="timeline-list">
              {workflow.data.map((item) => (
                <li key={item.id}>
                  <div>
                    <strong>{item.action.replace(/_/g, " ")}</strong>
                    <p>{item.comments || `${item.from_state || "new"} to ${item.to_state || "updated"}`}</p>
                  </div>
                  <span>{formatDateTime(item.created_at)}</span>
                </li>
              ))}
            </ul>
          )}
        </SectionCard>
      </section>
    </div>
  );
}
