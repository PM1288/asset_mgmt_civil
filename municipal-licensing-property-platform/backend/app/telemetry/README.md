# telemetry

## Purpose

Prometheus metrics definitions exposed by the API.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- `GET /metrics`

## Dependencies

- prometheus_client
- middleware
- background tasks

## Operational notes

- Protect /metrics at the network layer in hardened production.

## Failure considerations

- Metrics failure should not block core business requests.
