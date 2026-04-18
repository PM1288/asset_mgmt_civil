from __future__ import annotations


def test_idempotent_property_create(client):
    payload = {
        "property_number": "PROP-1002",
        "ward_code": "A2",
        "address_line_1": "2 FC Road",
        "city": "Pune",
        "district": "Pune",
        "state": "Maharashtra",
        "status": "active",
        "use_type": "residential",
        "owner_name": "Owner Two",
    }
    headers = {"Idempotency-Key": "p-2"}
    first = client.post("/api/v1/properties", json=payload, headers=headers)
    second = client.post("/api/v1/properties", json=payload, headers=headers)
    assert first.status_code == 201
    assert second.status_code == 201
