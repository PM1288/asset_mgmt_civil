from __future__ import annotations


def _create_property(client, property_number: str):
    response = client.post(
        "/api/v1/properties",
        json={
            "property_number": property_number,
            "ward_code": "A1",
            "address_line_1": "1 MG Road",
            "city": "Pune",
            "district": "Pune",
            "state": "Maharashtra",
            "status": "active",
            "use_type": "commercial",
            "owner_name": "Demo Owner",
            "owner_contact": "9999999999",
        },
        headers={"Idempotency-Key": f"{property_number}-create"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_license(client, property_id: str, application_number: str):
    response = client.post(
        "/api/v1/licenses",
        json={
            "application_number": application_number,
            "property_id": property_id,
            "license_type": "trade",
            "applicant_name": "Demo Applicant",
            "applicant_contact": "9000000000",
            "notes": "Created by test",
        },
        headers={"Idempotency-Key": f"{application_number}-create"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_dashboard_summary_and_recent_activity(client):
    property_record = _create_property(client, "PROP-2001")
    license_record = _create_license(client, property_record["id"], "LIC-2001")

    client.post(f"/api/v1/licenses/{license_record['id']}/submit", json={"comments": "Submitted for review"})
    client.post(
        f"/api/v1/licenses/{license_record['id']}/review",
        json={"comments": "Review in progress", "assignee": "officer-a1"},
    )

    summary = client.get("/api/v1/dashboard/summary")
    assert summary.status_code == 200, summary.text
    summary_body = summary.json()
    assert summary_body["total_properties"] >= 1
    assert summary_body["licenses_pending_review"] >= 1

    queues = client.get("/api/v1/dashboard/queues")
    assert queues.status_code == 200, queues.text
    queue_keys = {item["key"] for item in queues.json()["items"]}
    assert {"submitted_unassigned", "under_review", "due_today", "overdue"} <= queue_keys

    recent = client.get("/api/v1/dashboard/recent-activity")
    assert recent.status_code == 200, recent.text
    recent_body = recent.json()
    assert any(item["entity_type"] == "license" for item in recent_body["records"])
    assert any(item["action"] == "review" for item in recent_body["workflow_transitions"])


def test_revoke_license_route(client):
    property_record = _create_property(client, "PROP-2002")
    license_record = _create_license(client, property_record["id"], "LIC-2002")

    client.post(f"/api/v1/licenses/{license_record['id']}/submit", json={"comments": "Submitted"})
    client.post(f"/api/v1/licenses/{license_record['id']}/review", json={"comments": "Reviewing"})
    client.post(f"/api/v1/licenses/{license_record['id']}/approve", json={"comments": "Approved"})
    revoked = client.post(f"/api/v1/licenses/{license_record['id']}/revoke", json={"comments": "Revoked"})

    assert revoked.status_code == 200, revoked.text
    assert revoked.json()["status"] == "revoked"
