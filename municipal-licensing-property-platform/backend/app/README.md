# app

## Purpose

Application package containing API routes, resilience primitives, configuration, services, persistence, and task code.

## Files and subfolders

- `api/`: Subdirectory for related implementation or documentation.
- `core/`: Subdirectory for related implementation or documentation.
- `db/`: Subdirectory for related implementation or documentation.
- `schemas/`: Subdirectory for related implementation or documentation.
- `services/`: Subdirectory for related implementation or documentation.
- `storage/`: Subdirectory for related implementation or documentation.
- `tasks/`: Subdirectory for related implementation or documentation.
- `telemetry/`: Subdirectory for related implementation or documentation.

## API endpoints implemented in this folder

- `/api/v1/*`
- `/health/*`
- `/metrics`

## Dependencies

- backend/alembic
- Docker environment variables
- runtime volumes

## Operational notes

- Keep module imports deterministic because startup depends on validated settings.

## Failure considerations

- Import-time config failures will prevent the ASGI application from loading.
