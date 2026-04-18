# app

## Purpose

Deployment state, release markers, and other small runtime control artifacts.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- No endpoints are implemented directly in this folder.

## Dependencies

- deploy_windows.ps1
- rollback_windows.ps1

## Operational notes

- Preserve release_state.json to keep rollback information intact.

## Failure considerations

- Deleting release markers impairs scripted rollback.
