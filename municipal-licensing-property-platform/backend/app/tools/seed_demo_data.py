from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.db.repositories.documents import DocumentRepository
from app.db.repositories.licenses import LicenseRepository
from app.db.repositories.properties import PropertyRepository
from app.db.session import SessionLocal
from app.schemas.license import LicenseAction, LicenseCreate
from app.schemas.property import PropertyCreate, PropertyUpdate
from app.services.document_service import document_service
from app.services.license_service import license_service
from app.services.property_service import property_service
from app.services.workflow_service import workflow_service


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _set_timestamps(entity, *, created_at: datetime, updated_at: datetime | None = None) -> None:
    entity.created_at = created_at
    entity.updated_at = updated_at or created_at


def _create_property(db: Session, *, property_number: str, ward_code: str, address: str, owner_name: str, use_type: str, status: str = "active"):
    record = property_service.create(
        db,
        payload=PropertyCreate(
            property_number=property_number,
            ward_code=ward_code,
            address_line_1=address,
            city="Pune",
            district="Pune",
            state="Maharashtra",
            status=status,
            use_type=use_type,
            owner_name=owner_name,
            owner_contact="9999999999",
            remarks=f"{use_type.title()} property in ward {ward_code}",
        ),
        actor="demo-seed",
        ip_address="127.0.0.1",
    )
    db.commit()
    return record


def _create_license(
    db: Session,
    *,
    application_number: str,
    property_id: str,
    license_type: str,
    applicant_name: str,
    transition_chain: list[tuple[str, LicenseAction]],
):
    record = license_service.create(
        db,
        payload=LicenseCreate(
            application_number=application_number,
            property_id=property_id,
            license_type=license_type,
            applicant_name=applicant_name,
            applicant_contact="9000000000",
            notes="Seeded municipal workload",
        ),
        actor="demo-seed",
        ip_address="127.0.0.1",
    )
    db.commit()

    for transition, action in transition_chain:
        record = license_service.transition(
            db,
            license_id=record.id,
            transition=transition,
            action=action,
            actor="demo-seed",
            ip_address="127.0.0.1",
        )
        db.commit()

    return record


def _upload_text_document(db: Session, *, aggregate_type: str, aggregate_id: str, property_id: str | None, license_id: str | None, filename: str, content: str) -> None:
    document_service.upload(
        db,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        property_id=property_id,
        license_id=license_id,
        filename=filename,
        media_type="text/plain",
        payload=content.encode("utf-8"),
        actor="demo-seed",
        ip_address="127.0.0.1",
    )
    db.commit()


def seed(db: Session, *, force: bool = False) -> dict[str, int]:
    property_repo = PropertyRepository()
    license_repo = LicenseRepository()
    document_repo = DocumentRepository()

    if property_repo.list(db) and not force:
        return {"properties": 0, "licenses": 0, "documents": 0, "skipped": 1}

    if force:
        # The deployment is for local/demo use only. Wipe in dependency order when reseeding.
        for document in document_repo.list_all(db):
            db.delete(document)
        for workflow in workflow_service.repo.list_recent(db, limit=1000):
            db.delete(workflow)
        for license_record in license_repo.list(db):
            db.delete(license_record)
        for property_record in property_repo.list(db):
            db.delete(property_record)
        db.commit()

    properties = [
        _create_property(
            db,
            property_number="PROP-2001",
            ward_code="A1",
            address="14 Riverfront Road",
            owner_name="Sharma Trading Company",
            use_type="commercial",
        ),
        _create_property(
            db,
            property_number="PROP-2002",
            ward_code="B2",
            address="18 Market Lane",
            owner_name="Mhatre Foods",
            use_type="restaurant",
        ),
        _create_property(
            db,
            property_number="PROP-2003",
            ward_code="C7",
            address="7 Industrial Estate",
            owner_name="Prakash Fabricators",
            use_type="industrial",
        ),
        _create_property(
            db,
            property_number="PROP-2004",
            ward_code="D4",
            address="3 Health Colony",
            owner_name="Sai Diagnostics",
            use_type="clinic",
        ),
        _create_property(
            db,
            property_number="PROP-2005",
            ward_code="E9",
            address="41 Station Road",
            owner_name="Kulkarni Warehousing",
            use_type="warehouse",
        ),
        _create_property(
            db,
            property_number="PROP-2006",
            ward_code="F3",
            address="22 Temple Street",
            owner_name="Joshi Retail",
            use_type="retail",
        ),
    ]

    properties_by_number = {item.property_number: item for item in property_repo.list(db)}
    now = _utc_now()

    property_offsets = {
        "PROP-2001": 45,
        "PROP-2002": 30,
        "PROP-2003": 21,
        "PROP-2004": 10,
        "PROP-2005": 5,
        "PROP-2006": 2,
    }
    for property_record in property_repo.list(db):
        created_at = now - timedelta(days=property_offsets[property_record.property_number])
        _set_timestamps(property_record, created_at=created_at, updated_at=created_at + timedelta(hours=2))
        db.add(property_record)
    db.commit()

    licenses = [
        _create_license(
            db,
            application_number="LIC-3001",
            property_id=properties_by_number["PROP-2001"].id,
            license_type="trade",
            applicant_name="Sharma Trading Company",
            transition_chain=[
                ("submit", LicenseAction(comments="Submitted for trade renewal")),
                ("review", LicenseAction(comments="Inspection slot requested", assignee="officer-a1")),
                ("approve", LicenseAction(comments="Approved after field check")),
            ],
        ),
        _create_license(
            db,
            application_number="LIC-3002",
            property_id=properties_by_number["PROP-2002"].id,
            license_type="health",
            applicant_name="Mhatre Foods",
            transition_chain=[
                ("submit", LicenseAction(comments="Submitted with kitchen plan")),
                ("review", LicenseAction(comments="Officer review started", assignee="officer-b2")),
            ],
        ),
        _create_license(
            db,
            application_number="LIC-3003",
            property_id=properties_by_number["PROP-2003"].id,
            license_type="fire",
            applicant_name="Prakash Fabricators",
            transition_chain=[
                ("submit", LicenseAction(comments="Awaiting fire audit")),
            ],
        ),
        _create_license(
            db,
            application_number="LIC-3004",
            property_id=properties_by_number["PROP-2004"].id,
            license_type="trade",
            applicant_name="Sai Diagnostics",
            transition_chain=[
                ("submit", LicenseAction(comments="Supporting documents missing")),
                ("review", LicenseAction(comments="Requested corrections", assignee="officer-d4")),
                ("reject", LicenseAction(comments="Applicant must upload revised floor plan")),
            ],
        ),
        _create_license(
            db,
            application_number="LIC-3005",
            property_id=properties_by_number["PROP-2005"].id,
            license_type="building",
            applicant_name="Kulkarni Warehousing",
            transition_chain=[
                ("submit", LicenseAction(comments="Warehouse expansion review")),
                ("review", LicenseAction(comments="Approved structurally", assignee="officer-e9")),
                ("approve", LicenseAction(comments="Occupancy clearance granted")),
                ("revoke", LicenseAction(comments="Safety violation recorded")),
            ],
        ),
        _create_license(
            db,
            application_number="LIC-3006",
            property_id=properties_by_number["PROP-2006"].id,
            license_type="trade",
            applicant_name="Joshi Retail",
            transition_chain=[],
        ),
    ]

    license_timeline = {
        "LIC-3001": {
            "created_days_ago": 345,
            "updated_days_after": 20,
            "submitted_hours_after": 4,
            "decided_days_after": 20,
        },
        "LIC-3002": {
            "created_days_ago": 5,
            "updated_days_after": 5,
            "submitted_hours_after": 2,
        },
        "LIC-3003": {
            "created_days_ago": 4,
            "updated_days_after": 1,
            "submitted_hours_after": 2,
        },
        "LIC-3004": {
            "created_days_ago": 11,
            "updated_days_after": 4,
            "submitted_hours_after": 2,
            "decided_days_after": 4,
        },
        "LIC-3005": {
            "created_days_ago": 400,
            "updated_days_after": 10,
            "submitted_hours_after": 2,
            "decided_days_after": 10,
        },
        "LIC-3006": {
            "created_days_ago": 1,
            "updated_days_after": 0,
        },
    }
    for license_record in license_repo.list(db):
        schedule = license_timeline[license_record.application_number]
        created_at = now - timedelta(days=schedule["created_days_ago"])
        updated_at = created_at + timedelta(days=schedule["updated_days_after"])
        _set_timestamps(license_record, created_at=created_at, updated_at=updated_at)
        submitted_hours_after = schedule.get("submitted_hours_after")
        decided_days_after = schedule.get("decided_days_after")
        if submitted_hours_after is not None:
            license_record.submitted_at = created_at + timedelta(hours=submitted_hours_after)
            updated_at = max(updated_at, license_record.submitted_at)
        else:
            license_record.submitted_at = None
        if decided_days_after is not None:
            license_record.decided_at = created_at + timedelta(days=decided_days_after)
            updated_at = max(updated_at, license_record.decided_at)
        else:
            license_record.decided_at = None
        license_record.updated_at = updated_at
        db.add(license_record)
    db.commit()

    _upload_text_document(
        db,
        aggregate_type="property",
        aggregate_id=properties_by_number["PROP-2001"].id,
        property_id=properties_by_number["PROP-2001"].id,
        license_id=None,
        filename="property-note.txt",
        content="Initial survey note for market inspection.",
    )
    _upload_text_document(
        db,
        aggregate_type="license",
        aggregate_id=license_repo.get_by_number(db, "LIC-3001").id,
        property_id=properties_by_number["PROP-2001"].id,
        license_id=license_repo.get_by_number(db, "LIC-3001").id,
        filename="trade-inspection.txt",
        content="Inspection cleared and fee confirmed.",
    )
    _upload_text_document(
        db,
        aggregate_type="license",
        aggregate_id=license_repo.get_by_number(db, "LIC-3002").id,
        property_id=properties_by_number["PROP-2002"].id,
        license_id=license_repo.get_by_number(db, "LIC-3002").id,
        filename="health-checklist.txt",
        content="Checklist received and queued for officer review.",
    )

    # Add one operator-visible follow-up event on a property timeline.
    property_target = property_repo.get_by_number(db, "PROP-2003")
    if property_target:
        property_service.update(
            db,
            property_id=property_target.id,
            payload=PropertyUpdate(remarks="Noise clearance pending from local ward office"),
            actor="demo-seed",
            ip_address="127.0.0.1",
        )
        db.commit()

    return {
        "properties": len(property_repo.list(db)),
        "licenses": len(license_repo.list(db)),
        "documents": len(document_repo.list_all(db)),
        "skipped": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo data for the municipal operator console.")
    parser.add_argument("--force", action="store_true", help="Replace existing demo data.")
    args = parser.parse_args()

    with SessionLocal() as db:
        result = seed(db, force=args.force)
    print(result)


if __name__ == "__main__":
    main()
