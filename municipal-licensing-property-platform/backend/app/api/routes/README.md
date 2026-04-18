# routes

## Purpose

Concrete endpoint implementations for auth, health, properties, licensing, documents, workflow, and admin operations.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- `GET /health/live`
- `GET /health/ready`
- `GET /health/startup`
- `GET /api/v1/auth/me`
- `GET/POST/PUT /api/v1/properties*`
- `GET/POST /api/v1/licenses*`
- `GET /api/v1/workflows/{aggregate_type}/{aggregate_id}`
- `GET /api/v1/documents/{document_id}/download`
- `GET/POST /api/v1/admin/*`

## Dependencies

- services/*
- schemas/*
- core/idempotency.py
- core/security.py

## Operational notes

- Unsafe create/update endpoints support idempotency keys.

## Failure considerations

- Role mapping or payload validation issues surface here first.
