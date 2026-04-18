# Municipal Licensing & Property Platform

A production-oriented, on-premises municipal workflow platform for property records, licensing workflows, encrypted document handling, auditability, scheduled maintenance, and validated backups.

## Why this repository exists

This repository implements a self-hosted reference platform for Maharashtra-style municipal property and licensing workflows. It is designed for Windows-hosted Docker deployments and assumes a controlled on-premises environment operated by a municipal IT team or SI partner.

## Core characteristics

- Self-hosted FastAPI backend with PostgreSQL, Redis, Celery, Keycloak, and Caddy.
- Secure-by-default identity with Keycloak, TOTP support, RBAC, optional LDAP federation path, and offline JWT validation.
- Encrypted document storage, structured logging, audit logging, health/readiness/liveness endpoints, and bounded operational behavior.
- Windows-oriented deployment scripts for build, deploy, smoke test, rollback, backup, restore, and package generation.
- Repository generator support through `create_project.py` so the complete codebase can be recreated elsewhere.

## Quick start

1. Copy `.env.example` to `.env`.
2. Run `scripts/generate_secrets.ps1` to populate local secrets.
3. Review `docs/deployment/windows-deployment.md`.
4. Run `scripts/deploy_windows.ps1`.
5. Run `scripts/healthcheck_smoke_test.ps1`.

## Default URLs

- End-user portal: `https://localhost:8443`
- API docs: `https://localhost:8443/docs`
- Keycloak login and realm UI: `https://localhost:8443/auth`

## Important operations

- Deploy: `scripts/deploy_windows.ps1`
- Rollback: `scripts/rollback_windows.ps1`
- Backup: `scripts/backup_db.ps1`
- Validate backup: `scripts/validate_backup.ps1`
- Restore backup: `scripts/restore_db.ps1`
- Package repository: `package_release.ps1`

## Design notes

This implementation uses Keycloak as the identity plane because it is mature, supports local user storage, TOTP, and LDAP federation. Caddy provides self-hosted TLS with an internal CA, making Windows Docker deployments simpler than managing PEM assets manually on day one. The backend uses encrypted fields for sensitive data and encrypted document storage on a mounted local volume to minimize operational complexity while preserving data confidentiality at rest.


## Root folder operational notes

- `docker-compose.yml` is the authoritative runtime topology.
- `.env.example` is a non-secret template and should be copied to `.env`.
- `package_release.ps1` creates a ZIP-ready package from the repository root.

## Root folder failure considerations

- A broken compose file or invalid environment can prevent the entire platform from starting.
- Removing `runtime/` without a backup destroys mutable operational state.
