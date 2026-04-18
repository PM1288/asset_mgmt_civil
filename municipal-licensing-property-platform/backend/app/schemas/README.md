# schemas

## Purpose

Pydantic request and response models used to validate API contracts.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- `Referenced by all route handlers under api/routes.`

## Dependencies

- API routes
- services
- FastAPI validation

## Operational notes

- Schema evolution must stay aligned with frontend expectations and migrations.

## Failure considerations

- Contract mismatch causes request rejection or invalid client assumptions.
