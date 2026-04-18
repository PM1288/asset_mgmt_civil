# frontend

## Purpose

React/Vite single-page application that authenticates through Keycloak and calls the backend through the same origin.

## Files and subfolders

- `public/`: Subdirectory for related implementation or documentation.
- `src/`: Subdirectory for related implementation or documentation.

## API endpoints implemented in this folder

- `Consumes backend endpoints; serves the browser UI.`

## Dependencies

- Keycloak
- API routes under /api/v1
- Caddy / Nginx

## Operational notes

- Build artifacts are static and served by Nginx inside the frontend image.

## Failure considerations

- Broken static build disables UI even if the API remains healthy.
