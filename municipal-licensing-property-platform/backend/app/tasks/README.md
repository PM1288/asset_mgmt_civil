# tasks

## Purpose

Celery application, worker tasks, and scheduler task definitions.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- No endpoints are implemented directly in this folder.

## Dependencies

- Redis
- services/backup_service.py
- services/maintenance_service.py

## Operational notes

- Beat schedules maintenance and backup jobs; worker executes them.

## Failure considerations

- Queue backlog or beat outage delays backups and cleanup.
