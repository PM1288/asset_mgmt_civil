# caddy

## Purpose

Caddy edge proxy configuration for HTTPS, compression, security headers, and upstream routing.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- `Routes /api/* and /health/* to api; routes / to frontend.`

## Dependencies

- proxy service in docker-compose.yml
- api and frontend upstreams

## Operational notes

- Default deployment uses internal TLS; replace with enterprise certs if required.

## Failure considerations

- Invalid upstream names or ports create full or partial outage.
