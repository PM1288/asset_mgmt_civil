"""initial schema"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("subject", sa.String(length=128), nullable=False),
        sa.Column("username", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=256), nullable=True),
        sa.Column("department", sa.String(length=128), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_profiles")),
    )
    op.create_index(op.f("ix_user_profiles_subject"), "user_profiles", ["subject"], unique=True)
    op.create_index(op.f("ix_user_profiles_username"), "user_profiles", ["username"], unique=False)

    op.create_table(
        "idempotency_records",
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("route", sa.String(length=255), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("response_body", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.String(length=64), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_idempotency_records")),
    )
    op.create_index(op.f("ix_idempotency_records_key"), "idempotency_records", ["key"], unique=True)

    op.create_table(
        "properties",
        sa.Column("property_number", sa.String(length=64), nullable=False),
        sa.Column("ward_code", sa.String(length=32), nullable=False),
        sa.Column("address_line_1", sa.String(length=255), nullable=False),
        sa.Column("address_line_2", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=128), nullable=False),
        sa.Column("district", sa.String(length=128), nullable=False),
        sa.Column("state", sa.String(length=128), nullable=False),
        sa.Column("postal_code", sa.String(length=16), nullable=True),
        sa.Column("geo_lat", sa.Float(), nullable=True),
        sa.Column("geo_lng", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("use_type", sa.String(length=64), nullable=False),
        sa.Column("owner_name_enc", sa.Text(), nullable=False),
        sa.Column("owner_contact_enc", sa.Text(), nullable=True),
        sa.Column("assessment_zone", sa.String(length=64), nullable=True),
        sa.Column("remarks_enc", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_properties")),
    )
    op.create_index(op.f("ix_properties_property_number"), "properties", ["property_number"], unique=True)
    op.create_index(op.f("ix_properties_ward_code"), "properties", ["ward_code"], unique=False)
    op.create_index("ix_properties_property_number_status", "properties", ["property_number", "status"], unique=False)

    op.create_table(
        "license_applications",
        sa.Column("application_number", sa.String(length=64), nullable=False),
        sa.Column("property_id", sa.String(length=36), nullable=False),
        sa.Column("license_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("applicant_name_enc", sa.Text(), nullable=False),
        sa.Column("applicant_contact_enc", sa.Text(), nullable=True),
        sa.Column("current_assignee", sa.String(length=128), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes_enc", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], name=op.f("fk_license_applications_property_id_properties"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_license_applications")),
    )
    op.create_index(op.f("ix_license_applications_application_number"), "license_applications", ["application_number"], unique=True)
    op.create_index(op.f("ix_license_applications_property_id"), "license_applications", ["property_id"], unique=False)
    op.create_index("ix_license_applications_application_number_status", "license_applications", ["application_number", "status"], unique=False)

    op.create_table(
        "workflow_events",
        sa.Column("aggregate_type", sa.String(length=32), nullable=False),
        sa.Column("aggregate_id", sa.String(length=36), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("from_state", sa.String(length=32), nullable=True),
        sa.Column("to_state", sa.String(length=32), nullable=True),
        sa.Column("actor_subject", sa.String(length=128), nullable=False),
        sa.Column("comments_enc", sa.Text(), nullable=True),
        sa.Column("license_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["license_id"], ["license_applications.id"], name=op.f("fk_workflow_events_license_id_license_applications"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflow_events")),
    )
    op.create_index("ix_workflow_events_aggregate", "workflow_events", ["aggregate_type", "aggregate_id"], unique=False)

    op.create_table(
        "documents",
        sa.Column("aggregate_type", sa.String(length=32), nullable=False),
        sa.Column("aggregate_id", sa.String(length=36), nullable=False),
        sa.Column("property_id", sa.String(length=36), nullable=True),
        sa.Column("license_id", sa.String(length=36), nullable=True),
        sa.Column("storage_path", sa.String(length=512), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("media_type", sa.String(length=128), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("uploaded_by", sa.String(length=128), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], name=op.f("fk_documents_property_id_properties"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["license_id"], ["license_applications.id"], name=op.f("fk_documents_license_id_license_applications"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_documents")),
        sa.UniqueConstraint("storage_path", name=op.f("uq_documents_storage_path")),
    )
    op.create_index("ix_documents_aggregate", "documents", ["aggregate_type", "aggregate_id"], unique=False)
    op.create_index(op.f("ix_documents_sha256"), "documents", ["sha256"], unique=False)

    op.create_table(
        "audit_events",
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("subject", sa.String(length=128), nullable=True),
        sa.Column("actor", sa.String(length=128), nullable=True),
        sa.Column("outcome", sa.String(length=32), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("detail_message", sa.Text(), nullable=True),
        sa.Column("details_json", sa.JSON(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_events")),
    )
    op.create_index(op.f("ix_audit_events_event_type"), "audit_events", ["event_type"], unique=False)
    op.create_index("ix_audit_events_created_event_type", "audit_events", ["created_at", "event_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_events_created_event_type", table_name="audit_events")
    op.drop_index(op.f("ix_audit_events_event_type"), table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index(op.f("ix_documents_sha256"), table_name="documents")
    op.drop_index("ix_documents_aggregate", table_name="documents")
    op.drop_table("documents")
    op.drop_index("ix_workflow_events_aggregate", table_name="workflow_events")
    op.drop_table("workflow_events")
    op.drop_index("ix_license_applications_application_number_status", table_name="license_applications")
    op.drop_index(op.f("ix_license_applications_property_id"), table_name="license_applications")
    op.drop_index(op.f("ix_license_applications_application_number"), table_name="license_applications")
    op.drop_table("license_applications")
    op.drop_index("ix_properties_property_number_status", table_name="properties")
    op.drop_index(op.f("ix_properties_ward_code"), table_name="properties")
    op.drop_index(op.f("ix_properties_property_number"), table_name="properties")
    op.drop_table("properties")
    op.drop_index(op.f("ix_idempotency_records_key"), table_name="idempotency_records")
    op.drop_table("idempotency_records")
    op.drop_index(op.f("ix_user_profiles_username"), table_name="user_profiles")
    op.drop_index(op.f("ix_user_profiles_subject"), table_name="user_profiles")
    op.drop_table("user_profiles")
