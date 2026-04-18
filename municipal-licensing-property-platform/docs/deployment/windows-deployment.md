# Windows Deployment

## Host prerequisites

- Windows 11 or Windows Server with Docker Desktop or Docker Engine + Compose plugin
- Git
- PowerShell 7 recommended
- Sufficient local disk for databases, documents, logs, and backups

## Procedure

1. Clone the repository or let `scripts/deploy_windows.ps1` do it.
2. Copy `.env.example` to `.env`.
3. Run `scripts/generate_secrets.ps1`.
4. Set `APP_HOSTNAME`, ports, and any site-specific values.
5. Run `scripts/deploy_windows.ps1`.
6. Run `scripts/healthcheck_smoke_test.ps1`.
7. Log into Keycloak through `https://<host>:8443/auth` and finalize user provisioning and TOTP enforcement.

## Rollback

Use:
- `scripts/rollback_windows.ps1`

Rollback depends on previous images still being available locally. Do not prune images immediately after a successful release.

## Upgrades

- Pull repository changes.
- Review migrations.
- Build new images with a new `RELEASE_TAG`.
- Run deployment script.
- Validate health and user journeys.
