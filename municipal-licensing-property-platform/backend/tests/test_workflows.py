from __future__ import annotations


def test_property_workflow_history_alias(client):
    payload = {
        "property_number": "PROP-WF-1001",
        "ward_code": "A1",
        "address_line_1": "1 Governance Avenue",
        "city": "Pune",
        "district": "Pune",
        "state": "Maharashtra",
        "status": "active",
        "use_type": "commercial",
        "owner_name": "Workflow Owner",
        "owner_contact": "9999999999",
    }
    created = client.post("/api/v1/properties", json=payload, headers={"Idempotency-Key": "wf-1"})
    assert created.status_code == 201, created.text
    property_id = created.json()["id"]

    direct = client.get(f"/api/v1/workflows/property/{property_id}")
    alias = client.get(f"/api/v1/workflows/property/{property_id}/history")

    assert direct.status_code == 200, direct.text
    assert alias.status_code == 200, alias.text
    assert alias.json() == direct.json()
    assert len(alias.json()) >= 1
