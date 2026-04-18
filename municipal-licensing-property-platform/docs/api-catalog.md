# API Catalog

Base API prefix: `/api/v1`

## Authentication and user context

| Endpoint | Method | Purpose | Auth |
|---|---|---|---|
| `/api/v1/auth/me` | GET | Returns current subject and roles | Any authenticated user |

## Property management

| Endpoint | Method | Purpose | Auth |
|---|---|---|---|
| `/api/v1/properties` | GET | List properties | admin, property-officer, auditor, viewer |
| `/api/v1/properties/{property_id}` | GET | Fetch one property | admin, property-officer, auditor, viewer |
| `/api/v1/properties` | POST | Create property record | admin, property-officer |
| `/api/v1/properties/{property_id}` | PUT | Update property record | admin, property-officer |
| `/api/v1/properties/{property_id}/documents` | GET | List property documents | admin, property-officer, auditor, viewer |
| `/api/v1/properties/{property_id}/documents` | POST | Upload property document | admin, property-officer |

## Licensing workflow

| Endpoint | Method | Purpose | Auth |
|---|---|---|---|
| `/api/v1/licenses` | GET | List applications | admin, licensing-officer, auditor, viewer |
| `/api/v1/licenses/{license_id}` | GET | Fetch one application | admin, licensing-officer, auditor, viewer |
| `/api/v1/licenses` | POST | Create application | admin, licensing-officer |
| `/api/v1/licenses/{license_id}/submit` | POST | Submit draft | admin, licensing-officer |
| `/api/v1/licenses/{license_id}/review` | POST | Move to review | admin, licensing-officer |
| `/api/v1/licenses/{license_id}/approve` | POST | Approve application | admin, licensing-officer |
| `/api/v1/licenses/{license_id}/reject` | POST | Reject application | admin, licensing-officer |
| `/api/v1/licenses/{license_id}/documents` | GET | List license documents | admin, licensing-officer, auditor, viewer |
| `/api/v1/licenses/{license_id}/documents` | POST | Upload license document | admin, licensing-officer |

## Workflow and document retrieval

| Endpoint | Method | Purpose | Auth |
|---|---|---|---|
| `/api/v1/workflows/{aggregate_type}/{aggregate_id}` | GET | Workflow history | admin, property-officer, licensing-officer, auditor, viewer |
| `/api/v1/documents/{document_id}/download` | GET | Download decrypted document stream | admin, property-officer, licensing-officer, auditor, viewer |

## Administration and operations

| Endpoint | Method | Purpose | Auth |
|---|---|---|---|
| `/api/v1/admin/audit` | GET | Recent audit log view | admin, auditor, operator |
| `/api/v1/admin/maintenance/cleanup` | POST | Execute retention cleanup | admin, operator |
| `/api/v1/admin/diagnostics/dependencies` | GET | Dependency health and disk stats | admin, operator, auditor |
| `/api/v1/admin/backups/run` | POST | Trigger backup bundle creation | admin, operator |
| `/api/v1/admin/backups/validate-latest` | POST | Validate most recent backup | admin, operator |

## Public health and telemetry

| Endpoint | Method | Purpose | Auth |
|---|---|---|---|
| `/health/live` | GET | Liveness probe | None |
| `/health/ready` | GET | Readiness probe | None |
| `/health/startup` | GET | Startup/preflight status | None |
| `/metrics` | GET | Prometheus metrics | None; protect at network layer in production |

## Error conventions

- `400` invalid request shape.
- `401` missing or invalid token.
- `403` insufficient privileges.
- `404` not found.
- `409` idempotency or workflow conflict.
- `413` upload too large.
- `415` unsupported media type.
- `429` rate limit exceeded.
- `503` dependency unavailable, including auth/JWKS refresh failure.

## Idempotency

`POST /api/v1/properties` and `POST /api/v1/licenses` accept `Idempotency-Key`. Reuse with identical body returns the previously persisted success payload. Reuse with a different body is rejected with `409`.
