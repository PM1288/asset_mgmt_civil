# api

## Purpose

FastAPI routing composition and request dependency definitions.

## Files and subfolders

- `routes/`: Subdirectory for related implementation or documentation.

## API endpoints implemented in this folder

- `All public and admin API endpoints are composed here.`

## Dependencies

- core/security.py
- db/session.py
- services/*

## Operational notes

- Route-level role checks are the primary RBAC enforcement layer.

## Failure considerations

- A broken dependency override or missing auth context will fail requests early.
