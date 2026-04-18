# logs

## Purpose

Mounted log directory for API, worker, and beat structured logs.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- No endpoints are implemented directly in this folder.

## Dependencies

- core/logging.py
- docker logging options

## Operational notes

- Rotation exists, but host-level disk monitoring is still required.

## Failure considerations

- Unchecked log growth can still exhaust the host over time.
