export type Subject = {
  subject: string;
  username: string;
  email?: string;
  roles: string[];
};

export type AppRole =
  | "municipal-admin"
  | "property-officer"
  | "licensing-officer"
  | "auditor"
  | "viewer"
  | "operator";

export type PropertyRecord = {
  id: string;
  property_number: string;
  ward_code: string;
  address_line_1: string;
  address_line_2?: string | null;
  city: string;
  district: string;
  state: string;
  postal_code?: string | null;
  geo_lat?: number | null;
  geo_lng?: number | null;
  status: string;
  use_type: string;
  owner_name: string;
  owner_contact?: string | null;
  assessment_zone?: string | null;
  remarks?: string | null;
  created_at: string;
  updated_at: string;
};

export type LicenseRecord = {
  id: string;
  application_number: string;
  property_id: string;
  license_type: string;
  status: string;
  applicant_name: string;
  applicant_contact?: string | null;
  current_assignee?: string | null;
  submitted_at?: string | null;
  decided_at?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
};

export type HealthEnvelope = {
  status: string;
  components: { name: string; ok: boolean; detail: string }[];
};

export type AuditLogRecord = {
  id: string;
  event_type: string;
  subject?: string | null;
  actor?: string | null;
  outcome: string;
  ip_address?: string | null;
  detail_message?: string | null;
  details_json?: Record<string, unknown> | null;
  created_at: string;
};

export type DashboardSummary = {
  total_properties: number;
  active_licenses: number;
  licenses_pending_review: number;
  approvals_due_today: number;
  overdue_renewals: number;
  unresolved_exceptions: number;
};

export type DashboardQueueItem = {
  key: string;
  label: string;
  count: number;
  severity: "ok" | "warning" | "critical";
  description: string;
};

export type DashboardQueues = {
  items: DashboardQueueItem[];
};

export type DashboardRecordActivity = {
  id: string;
  entity_type: "property" | "license";
  title: string;
  subtitle: string;
  status: string;
  route: string;
  occurred_at: string;
};

export type DashboardWorkflowActivity = {
  id: string;
  aggregate_type: string;
  aggregate_id: string;
  action: string;
  from_state?: string | null;
  to_state?: string | null;
  actor_subject: string;
  comments?: string | null;
  route: string;
  occurred_at: string;
};

export type DashboardDocumentActivity = {
  id: string;
  aggregate_type: string;
  aggregate_id: string;
  original_filename: string;
  media_type: string;
  uploaded_by: string;
  route: string;
  occurred_at: string;
};

export type DashboardMissingEvidence = {
  license_id: string;
  application_number: string;
  property_id: string;
  license_type: string;
  status: string;
  route: string;
  detail: string;
};

export type DashboardRecentActivity = {
  records: DashboardRecordActivity[];
  workflow_transitions: DashboardWorkflowActivity[];
  latest_uploads: DashboardDocumentActivity[];
  missing_evidence: DashboardMissingEvidence[];
};

export type DashboardRenewalItem = {
  id: string;
  application_number: string;
  property_id: string;
  applicant_name: string;
  license_type: string;
  status: string;
  estimated_expiry_at: string;
  days_until_expiry: number;
  route: string;
};

export type DashboardComplianceItem = {
  id: string;
  application_number: string;
  property_id: string;
  applicant_name: string;
  license_type: string;
  status: string;
  occurred_at: string;
  route: string;
};

export type DashboardCompliance = {
  upcoming_renewals: DashboardRenewalItem[];
  recently_rejected: DashboardComplianceItem[];
  revoked_items: DashboardComplianceItem[];
};

export type DashboardHealthDependency = {
  key: string;
  label: string;
  status: "ok" | "warning" | "critical";
  detail: string;
};

export type DashboardHealthSignal = {
  key: string;
  label: string;
  status: "ok" | "warning" | "critical";
  value: string;
};

export type DashboardHealthSummary = {
  overall_status: "ok" | "degraded" | "critical";
  dependencies: DashboardHealthDependency[];
  signals: DashboardHealthSignal[];
};

export type WorkflowEventRecord = {
  id: string;
  aggregate_type: string;
  aggregate_id: string;
  action: string;
  from_state?: string | null;
  to_state?: string | null;
  actor_subject: string;
  comments?: string | null;
  created_at: string;
};

export type DocumentRecord = {
  id: string;
  aggregate_type: string;
  aggregate_id: string;
  storage_path: string;
  original_filename: string;
  media_type: string;
  sha256: string;
  size_bytes: number;
  uploaded_by: string;
  created_at: string;
};

export type DiagnosticsPayload = {
  readiness: HealthEnvelope;
  disk: {
    total_mb: number;
    used_mb: number;
    free_mb: number;
  };
  limits: {
    disk_pressure_threshold_percent: number;
    minimum_free_disk_mb: number;
  };
};
