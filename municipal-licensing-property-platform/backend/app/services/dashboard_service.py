from __future__ import annotations

import shutil
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.encryption import decrypt_value
from app.db.models import DocumentRecord, LicenseApplication
from app.db.repositories.documents import DocumentRepository
from app.db.repositories.licenses import LicenseRepository
from app.db.repositories.properties import PropertyRepository
from app.db.repositories.workflows import WorkflowRepository
from app.schemas.dashboard import (
    DashboardComplianceItemOut,
    DashboardComplianceOut,
    DashboardDocumentActivityOut,
    DashboardHealthDependencyOut,
    DashboardHealthSignalOut,
    DashboardHealthSummaryOut,
    DashboardMissingEvidenceOut,
    DashboardQueuesOut,
    DashboardQueueItemOut,
    DashboardRecentActivityOut,
    DashboardRecordActivityOut,
    DashboardRenewalItemOut,
    DashboardSummaryOut,
    DashboardWorkflowActivityOut,
)
from app.services.health_service import health_service

settings = get_settings()

REVIEW_SLA_DAYS = {
    "submitted": 2,
    "under_review": 5,
}

RENEWAL_WINDOWS_DAYS = {
    "trade": 365,
    "health": 365,
    "fire": 365,
    "signage": 365,
    "building": 730,
}

INSPECTION_LICENSE_TYPES = {"trade", "building", "fire", "occupancy"}


class DashboardService:
    def __init__(self) -> None:
        self.properties = PropertyRepository()
        self.licenses = LicenseRepository()
        self.documents = DocumentRepository()
        self.workflows = WorkflowRepository()

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _review_due_at(self, license_record: LicenseApplication) -> datetime | None:
        sla_days = REVIEW_SLA_DAYS.get(license_record.status)
        if sla_days is None:
            return None
        anchor = license_record.submitted_at or license_record.updated_at or license_record.created_at
        return anchor + timedelta(days=sla_days)

    def _estimated_expiry_at(self, license_record: LicenseApplication) -> datetime | None:
        if license_record.status not in {"approved", "revoked"}:
            return None
        anchor = license_record.decided_at or license_record.updated_at or license_record.created_at
        duration_days = RENEWAL_WINDOWS_DAYS.get(license_record.license_type, 365)
        return anchor + timedelta(days=duration_days)

    def _license_route(self, license_id: str) -> str:
        return f"/licenses/{license_id}"

    def _property_route(self, property_id: str) -> str:
        return f"/properties/{property_id}"

    def _documents_by_license(self, db: Session) -> dict[str, list[DocumentRecord]]:
        grouped: dict[str, list[DocumentRecord]] = {}
        for document in self.documents.list_all(db):
            if not document.license_id:
                continue
            grouped.setdefault(document.license_id, []).append(document)
        return grouped

    def summary(self, db: Session) -> DashboardSummaryOut:
        now = self._now()
        licenses = self.licenses.list(db)
        properties = self.properties.list(db)
        documents_by_license = self._documents_by_license(db)
        readiness = health_service.readiness(db)

        approvals_due_today = 0
        overdue_renewals = 0
        missing_evidence = 0

        for license_record in licenses:
            due_at = self._review_due_at(license_record)
            if due_at and due_at.date() == now.date():
                approvals_due_today += 1

            expiry_at = self._estimated_expiry_at(license_record)
            if expiry_at and expiry_at < now and license_record.status == "approved":
                overdue_renewals += 1

            if (
                license_record.status in {"submitted", "under_review"}
                and not documents_by_license.get(license_record.id)
            ):
                missing_evidence += 1

        unresolved_exceptions = (
            sum(1 for license_record in licenses if license_record.status in {"rejected", "revoked"})
            + missing_evidence
            + sum(1 for component in readiness.components if not component.ok)
        )

        return DashboardSummaryOut(
            total_properties=len(properties),
            active_licenses=sum(1 for license_record in licenses if license_record.status == "approved"),
            licenses_pending_review=sum(
                1 for license_record in licenses if license_record.status in {"submitted", "under_review"}
            ),
            approvals_due_today=approvals_due_today,
            overdue_renewals=overdue_renewals,
            unresolved_exceptions=unresolved_exceptions,
        )

    def queues(self, db: Session) -> DashboardQueuesOut:
        now = self._now()
        licenses = self.licenses.list(db)
        documents_by_license = self._documents_by_license(db)

        counts = {
            "submitted_unassigned": sum(
                1
                for license_record in licenses
                if license_record.status == "submitted" and not license_record.current_assignee
            ),
            "under_review": sum(1 for license_record in licenses if license_record.status == "under_review"),
            "waiting_for_inspection": sum(
                1
                for license_record in licenses
                if license_record.status in {"submitted", "under_review"}
                and license_record.license_type in INSPECTION_LICENSE_TYPES
                and not documents_by_license.get(license_record.id)
            ),
            "waiting_for_applicant_response": sum(
                1 for license_record in licenses if license_record.status == "rejected"
            ),
            "due_today": sum(
                1
                for license_record in licenses
                if (due_at := self._review_due_at(license_record)) is not None and due_at.date() == now.date()
            ),
            "overdue": sum(
                1
                for license_record in licenses
                if (due_at := self._review_due_at(license_record)) is not None and due_at.date() < now.date()
            ),
        }

        def severity_for_count(count: int, *, warning_threshold: int = 1, critical_threshold: int = 3) -> str:
            if count >= critical_threshold:
                return "critical"
            if count >= warning_threshold:
                return "warning"
            return "ok"

        return DashboardQueuesOut(
            items=[
                DashboardQueueItemOut(
                    key="submitted_unassigned",
                    label="Submitted but unassigned",
                    count=counts["submitted_unassigned"],
                    severity=severity_for_count(counts["submitted_unassigned"]),
                    description="Applications waiting for an officer assignment.",
                ),
                DashboardQueueItemOut(
                    key="under_review",
                    label="Under review",
                    count=counts["under_review"],
                    severity=severity_for_count(counts["under_review"]),
                    description="Applications currently being reviewed by licensing staff.",
                ),
                DashboardQueueItemOut(
                    key="waiting_for_inspection",
                    label="Waiting for inspection",
                    count=counts["waiting_for_inspection"],
                    severity=severity_for_count(counts["waiting_for_inspection"]),
                    description="Inspection-oriented applications without supporting evidence yet.",
                ),
                DashboardQueueItemOut(
                    key="waiting_for_applicant_response",
                    label="Waiting for applicant response",
                    count=counts["waiting_for_applicant_response"],
                    severity=severity_for_count(counts["waiting_for_applicant_response"]),
                    description="Rejected items awaiting corrected submissions from applicants.",
                ),
                DashboardQueueItemOut(
                    key="due_today",
                    label="Due today",
                    count=counts["due_today"],
                    severity=severity_for_count(counts["due_today"]),
                    description="Pending reviews that hit their target date today.",
                ),
                DashboardQueueItemOut(
                    key="overdue",
                    label="Overdue",
                    count=counts["overdue"],
                    severity=severity_for_count(counts["overdue"], warning_threshold=1, critical_threshold=2),
                    description="Pending reviews already outside the current service window.",
                ),
            ]
        )

    def recent_activity(self, db: Session) -> DashboardRecentActivityOut:
        properties = self.properties.list(db)
        licenses = self.licenses.list(db)
        latest_documents = self.documents.list_recent(db, limit=10)
        recent_workflows = self.workflows.list_recent(db, limit=10)
        documents_by_license = self._documents_by_license(db)

        record_items: list[DashboardRecordActivityOut] = []
        for property_record in properties[:10]:
            record_items.append(
                DashboardRecordActivityOut(
                    id=property_record.id,
                    entity_type="property",
                    title=property_record.property_number,
                    subtitle=f"Ward {property_record.ward_code} · {property_record.address_line_1}",
                    status=property_record.status,
                    route=self._property_route(property_record.id),
                    occurred_at=property_record.updated_at,
                )
            )
        for license_record in licenses[:10]:
            record_items.append(
                DashboardRecordActivityOut(
                    id=license_record.id,
                    entity_type="license",
                    title=license_record.application_number,
                    subtitle=f"{license_record.license_type.title()} · {decrypt_value(license_record.applicant_name_enc) or 'Applicant'}",
                    status=license_record.status,
                    route=self._license_route(license_record.id),
                    occurred_at=license_record.updated_at,
                )
            )

        record_items.sort(key=lambda item: item.occurred_at, reverse=True)

        workflow_items = [
            DashboardWorkflowActivityOut(
                id=item.id,
                aggregate_type=item.aggregate_type,
                aggregate_id=item.aggregate_id,
                action=item.action,
                from_state=item.from_state,
                to_state=item.to_state,
                actor_subject=item.actor_subject,
                comments=decrypt_value(item.comments_enc),
                route=self._license_route(item.aggregate_id)
                if item.aggregate_type == "license"
                else self._property_route(item.aggregate_id),
                occurred_at=item.created_at,
            )
            for item in recent_workflows
        ]

        document_items = [
            DashboardDocumentActivityOut(
                id=document.id,
                aggregate_type=document.aggregate_type,
                aggregate_id=document.aggregate_id,
                original_filename=document.original_filename,
                media_type=document.media_type,
                uploaded_by=document.uploaded_by,
                route=self._license_route(document.aggregate_id)
                if document.aggregate_type == "license"
                else self._property_route(document.aggregate_id),
                occurred_at=document.created_at,
            )
            for document in latest_documents
        ]

        missing_evidence_items = [
            DashboardMissingEvidenceOut(
                license_id=license_record.id,
                application_number=license_record.application_number,
                property_id=license_record.property_id,
                license_type=license_record.license_type,
                status=license_record.status,
                route=self._license_route(license_record.id),
                detail="No supporting documents uploaded for a pending application.",
            )
            for license_record in licenses
            if license_record.status in {"submitted", "under_review"} and not documents_by_license.get(license_record.id)
        ][:10]

        return DashboardRecentActivityOut(
            records=record_items[:10],
            workflow_transitions=workflow_items,
            latest_uploads=document_items,
            missing_evidence=missing_evidence_items,
        )

    def compliance(self, db: Session) -> DashboardComplianceOut:
        now = self._now()
        licenses = self.licenses.list(db)

        upcoming: list[DashboardRenewalItemOut] = []
        recently_rejected: list[DashboardComplianceItemOut] = []
        revoked_items: list[DashboardComplianceItemOut] = []

        for license_record in licenses:
            applicant_name = decrypt_value(license_record.applicant_name_enc) or "Applicant"
            expiry_at = self._estimated_expiry_at(license_record)
            if expiry_at and license_record.status == "approved":
                days_until_expiry = int((expiry_at.date() - now.date()).days)
                if days_until_expiry <= 45:
                    upcoming.append(
                        DashboardRenewalItemOut(
                            id=license_record.id,
                            application_number=license_record.application_number,
                            property_id=license_record.property_id,
                            applicant_name=applicant_name,
                            license_type=license_record.license_type,
                            status=license_record.status,
                            estimated_expiry_at=expiry_at,
                            days_until_expiry=days_until_expiry,
                            route=self._license_route(license_record.id),
                        )
                    )

            if license_record.status == "rejected":
                recently_rejected.append(
                    DashboardComplianceItemOut(
                        id=license_record.id,
                        application_number=license_record.application_number,
                        property_id=license_record.property_id,
                        applicant_name=applicant_name,
                        license_type=license_record.license_type,
                        status=license_record.status,
                        occurred_at=license_record.updated_at,
                        route=self._license_route(license_record.id),
                    )
                )

            if license_record.status == "revoked":
                revoked_items.append(
                    DashboardComplianceItemOut(
                        id=license_record.id,
                        application_number=license_record.application_number,
                        property_id=license_record.property_id,
                        applicant_name=applicant_name,
                        license_type=license_record.license_type,
                        status=license_record.status,
                        occurred_at=license_record.updated_at,
                        route=self._license_route(license_record.id),
                    )
                )

        upcoming.sort(key=lambda item: item.estimated_expiry_at)
        recently_rejected.sort(key=lambda item: item.occurred_at, reverse=True)
        revoked_items.sort(key=lambda item: item.occurred_at, reverse=True)

        return DashboardComplianceOut(
            upcoming_renewals=upcoming[:10],
            recently_rejected=recently_rejected[:10],
            revoked_items=revoked_items[:10],
        )

    def health_summary(self, db: Session) -> DashboardHealthSummaryOut:
        readiness = health_service.readiness(db)
        usage = shutil.disk_usage(settings.docs_root)
        used_percent = round((usage.used / usage.total) * 100, 1) if usage.total else 0.0
        free_mb = usage.free // (1024 * 1024)

        dependencies = [
            DashboardHealthDependencyOut(
                key=component.name,
                label=component.name.replace("-", " ").title(),
                status="ok" if component.ok else "warning",
                detail=component.detail,
            )
            for component in readiness.components
        ]

        disk_status = "ok"
        if used_percent >= settings.disk_pressure_threshold_percent or free_mb < settings.minimum_free_disk_mb:
            disk_status = "warning"
        if used_percent >= settings.disk_pressure_threshold_percent + 5 or free_mb < settings.minimum_free_disk_mb // 2:
            disk_status = "critical"

        signals = [
            DashboardHealthSignalOut(
                key="disk_usage",
                label="Document storage",
                status=disk_status,
                value=f"{used_percent}% used · {free_mb} MB free",
            ),
            DashboardHealthSignalOut(
                key="dependency_failures",
                label="Dependency failures",
                status="critical" if any(not component.ok for component in readiness.components) else "ok",
                value=str(sum(1 for component in readiness.components if not component.ok)),
            ),
        ]

        overall_status = "degraded" if any(not component.ok for component in readiness.components) else "ok"
        if any(signal.status == "critical" for signal in signals):
            overall_status = "critical"

        return DashboardHealthSummaryOut(
            overall_status=overall_status,
            dependencies=dependencies,
            signals=signals,
        )


dashboard_service = DashboardService()
