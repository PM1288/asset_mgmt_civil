# api

## Purpose

Typed frontend API wrappers around fetch and Keycloak bearer tokens.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- `Calls /api/v1/auth/me, /api/v1/properties, /api/v1/licenses, /health/ready, /api/v1/admin/diagnostics/dependencies`

## Dependencies

- auth/keycloak.ts
- backend API contracts

## Operational notes

- Token refresh happens here before API calls are made.

## Failure considerations

- A bug here can break every screen at once.
