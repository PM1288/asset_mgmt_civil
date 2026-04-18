# scripts

## Purpose

Windows-friendly operational scripts for deploy, rollback, migrations, smoke checks, backup, restore, cleanup, secret generation, and packaging.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- `Indirectly exercises health and admin endpoints during deployment validation.`

## Dependencies

- PowerShell
- Docker Compose
- Git
- .env

## Operational notes

- Prefer PowerShell 7. Run from repository root unless otherwise documented.

## Failure considerations

- Script failures are usually safe-stopping and should not be bypassed blindly.
