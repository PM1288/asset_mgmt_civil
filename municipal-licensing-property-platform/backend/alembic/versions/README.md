# versions

## Purpose

Versioned Alembic migration files.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- No endpoints are implemented directly in this folder.

## Dependencies

- alembic env
- database schema

## Operational notes

- Each file is an ordered schema change. Never edit an applied migration in place.

## Failure considerations

- Editing historical migrations can make recovery and audit trails unreliable.
