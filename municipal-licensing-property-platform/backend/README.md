# backend

## Purpose

Python backend service layer, data access layer, migrations, and tests.

## Files and subfolders

- `alembic/`: Subdirectory for related implementation or documentation.
- `app/`: Subdirectory for related implementation or documentation.
- `tests/`: Subdirectory for related implementation or documentation.

## API endpoints implemented in this folder

- `Implemented under app/api/routes`

## Dependencies

- PostgreSQL
- Redis
- Keycloak
- runtime document and backup mounts

## Operational notes

- Builds into the API image used by api, worker, beat, and migrations services.
- Requires APP_ENCRYPTION_KEY and database connectivity at startup.

## Failure considerations

- Missing secrets or low disk space will fail startup preflight.
- Migration drift will block deployment.
