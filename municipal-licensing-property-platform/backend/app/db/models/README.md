# models

## Purpose

Relational data models for properties, licenses, workflow events, documents, audit events, user profiles, and idempotency.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- No endpoints are implemented directly in this folder.

## Dependencies

- db/base.py
- Alembic initial migration

## Operational notes

- Keep encrypted fields opaque at this layer; decrypt only in services.

## Failure considerations

- Incorrect column or relationship changes can break migrations and queries.
