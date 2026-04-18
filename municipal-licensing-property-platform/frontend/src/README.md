# src

## Purpose

Frontend source tree containing API helpers, Keycloak bootstrapping, components, pages, and styling.

## Files and subfolders

- `api/`: Subdirectory for related implementation or documentation.
- `auth/`: Subdirectory for related implementation or documentation.
- `components/`: Subdirectory for related implementation or documentation.
- `hooks/`: Subdirectory for related implementation or documentation.
- `pages/`: Subdirectory for related implementation or documentation.
- `styles/`: Subdirectory for related implementation or documentation.
- `types/`: Subdirectory for related implementation or documentation.

## API endpoints implemented in this folder

- `Consumes /api/v1/*, /health/*, and /metrics indirectly through UI.`

## Dependencies

- browser runtime
- frontend package dependencies
- backend API contracts

## Operational notes

- Keep client-side assumptions aligned with backend schemas.

## Failure considerations

- Auth or fetch failures surface as UI errors first.
