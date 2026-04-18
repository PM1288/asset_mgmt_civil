# core

## Purpose

Core runtime concerns: config loading, logging, security, retries, rate limiting, middleware, startup checks, and helper primitives.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- No endpoints are implemented directly in this folder.

## Dependencies

- Environment variables
- Keycloak JWKS
- Redis
- filesystem

## Operational notes

- Treat this folder as the operational safety layer of the backend.

## Failure considerations

- Misconfiguration here usually affects every endpoint, not just one module.
