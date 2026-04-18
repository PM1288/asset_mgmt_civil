# repositories

## Purpose

Thin data-access abstractions for common CRUD/query patterns.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- No endpoints are implemented directly in this folder.

## Dependencies

- db/models
- SQLAlchemy Session

## Operational notes

- Repositories intentionally avoid business logic; keep transactions in services/routes.

## Failure considerations

- Incorrect filtering or missing indexes causes latent performance issues.
