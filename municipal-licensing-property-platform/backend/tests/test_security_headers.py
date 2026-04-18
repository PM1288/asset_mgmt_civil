from __future__ import annotations


def test_security_headers_present(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
