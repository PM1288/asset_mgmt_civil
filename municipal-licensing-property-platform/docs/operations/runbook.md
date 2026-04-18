# Operational Runbook

## Daily

- Review `/health/ready`.
- Review Docker container health and restart counts.
- Check disk utilization under `runtime/`.
- Confirm the latest backup exists and validate it on schedule.

## Weekly

- Run `scripts/validate_backup.ps1` against the most recent backup.
- Review `runtime/logs/` growth and confirm rotation behavior.
- Review Keycloak admin events and user onboarding/offboarding.

## Monthly

- Test rollback procedure on a non-production environment.
- Review role assignments and privileged accounts.
- Review data retention and archive policy.
- Review document volume and backup volume growth.

## Incident handling

### API unhealthy
1. Check `docker compose ps`.
2. Inspect `runtime/logs/api`.
3. Check `/health/ready`.
4. Verify database and Redis health.
5. If a release issue is confirmed, execute `scripts/rollback_windows.ps1`.

### Database unavailable
1. Stop write traffic if possible.
2. Verify container and volume health.
3. Restore from the latest validated backup if corruption is confirmed.
4. Re-run smoke tests.

### Auth unavailable
1. Verify Keycloak and keycloak-db containers.
2. Confirm realm import and database connectivity.
3. Existing JWT validation may continue temporarily if JWKS cache is warm.
4. New logins remain unavailable until the auth plane is restored.

### Disk pressure
1. Validate backup completion.
2. Prune obsolete backups beyond retention.
3. Archive long-lived data externally if policy permits.
4. Expand the host volume before restarting high-write workloads.
