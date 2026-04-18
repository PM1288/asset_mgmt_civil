# tests

## Purpose

Backend tests covering health, property creation, idempotency, and security headers.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- No endpoints are implemented directly in this folder.

## Dependencies

- pytest
- FastAPI TestClient
- SQLite in-memory test engine

## Operational notes

- Use tests as a release gate before packaging images.

## Failure considerations

- Tests do not replace full integration or DR exercises.
