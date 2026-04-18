# keycloak

## Purpose

Keycloak realm bootstrap assets and identity configuration templates.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- No endpoints are implemented directly in this folder.

## Dependencies

- keycloak container
- scripts/bootstrap_keycloak.ps1

## Operational notes

- Realm export is imported at first Keycloak startup.

## Failure considerations

- Client redirect mismatch or role drift causes authentication failures or privilege gaps.
