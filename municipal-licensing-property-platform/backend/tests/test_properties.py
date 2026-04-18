from __future__ import annotations


def test_create_and_list_property(client):
    payload = {
        "property_number": "PROP-1001",
        "ward_code": "A1",
        "address_line_1": "1 MG Road",
        "city": "Pune",
        "district": "Pune",
        "state": "Maharashtra",
        "status": "active",
        "use_type": "commercial",
        "owner_name": "Demo Owner",
        "owner_contact": "9999999999",
    }
    created = client.post("/api/v1/properties", json=payload, headers={"Idempotency-Key": "p-1"})
    assert created.status_code == 201, created.text
    listed = client.get("/api/v1/properties")
    assert listed.status_code == 200
    data = listed.json()
    assert len(data) >= 1
    assert data[0]["property_number"] == "PROP-1001"
