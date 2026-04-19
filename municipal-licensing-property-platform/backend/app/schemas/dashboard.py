from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DashboardSummaryOut(BaseModel):
    total_properties: int
    active_licenses: int
    licenses_pending_review: int
    approvals_due_today: int
    overdue_renewals: int
    unresolved_exceptions: int


class DashboardQueueItemOut(BaseModel):
    key: str
    label: str
    count: int
    severity: str
    description: str


class DashboardQueuesOut(BaseModel):
    items: list[DashboardQueueItemOut]


class DashboardRecordActivityOut(BaseModel):
    id: str
    entity_type: str
    title: str
    subtitle: str
    status: str
    route: str
    occurred_at: datetime


class DashboardWorkflowActivityOut(BaseModel):
    id: str
    aggregate_type: str
    aggregate_id: str
    action: str
    from_state: str | None
    to_state: str | None
    actor_subject: str
    comments: str | None
    route: str
    occurred_at: datetime


class DashboardDocumentActivityOut(BaseModel):
    id: str
    aggregate_type: str
    aggregate_id: str
    original_filename: str
    media_type: str
    uploaded_by: str
    route: str
    occurred_at: datetime


class DashboardMissingEvidenceOut(BaseModel):
    license_id: str
    application_number: str
    property_id: str
    license_type: str
    status: str
    route: str
    detail: str


class DashboardRecentActivityOut(BaseModel):
    records: list[DashboardRecordActivityOut]
    workflow_transitions: list[DashboardWorkflowActivityOut]
    latest_uploads: list[DashboardDocumentActivityOut]
    missing_evidence: list[DashboardMissingEvidenceOut]


class DashboardRenewalItemOut(BaseModel):
    id: str
    application_number: str
    property_id: str
    applicant_name: str
    license_type: str
    status: str
    estimated_expiry_at: datetime
    days_until_expiry: int
    route: str


class DashboardComplianceItemOut(BaseModel):
    id: str
    application_number: str
    property_id: str
    applicant_name: str
    license_type: str
    status: str
    occurred_at: datetime
    route: str


class DashboardComplianceOut(BaseModel):
    upcoming_renewals: list[DashboardRenewalItemOut]
    recently_rejected: list[DashboardComplianceItemOut]
    revoked_items: list[DashboardComplianceItemOut]


class DashboardHealthDependencyOut(BaseModel):
    key: str
    label: str
    status: str
    detail: str


class DashboardHealthSignalOut(BaseModel):
    key: str
    label: str
    status: str
    value: str


class DashboardHealthSummaryOut(BaseModel):
    overall_status: str
    dependencies: list[DashboardHealthDependencyOut]
    signals: list[DashboardHealthSignalOut]
