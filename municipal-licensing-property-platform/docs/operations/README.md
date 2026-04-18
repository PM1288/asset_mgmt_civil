# operations

## Purpose

Runbooks for backups, restore, maintenance, and disaster recovery.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- No endpoints are implemented directly in this folder.

## Dependencies

- scripts/*
- services/backup_service.py
- docker-compose.yml

## Operational notes

- Use these documents during drills and incidents, not only during design review.

## Failure considerations

- Skipping drills leaves restore risk undiscovered until an outage.
