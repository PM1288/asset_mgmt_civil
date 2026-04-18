# services

## Purpose

Business services for properties, licensing, workflow, documents, audit, health, maintenance, and backups.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- `Invoked by routes under /api/v1/* and by background tasks.`

## Dependencies

- repositories
- core/encryption
- storage
- telemetry

## Operational notes

- This layer owns domain rules, audit emission, and data transformation.

## Failure considerations

- Service bugs can corrupt workflow state or audit completeness.
