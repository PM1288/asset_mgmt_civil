# Compliance Matrix

| Requirement | Architecture decision | Feature(s) | File(s) / module(s) | Operational control | Evidence / test | Residual risk |
|---|---|---|---|---|---|---|
| Fully self-hosted | Compose-based stack with local services only | Caddy, Keycloak, Postgres, Redis, FastAPI, React | `docker-compose.yml` | Local Docker deployment | smoke test + compose inventory | Single-host design, not HA |
| Secure auth | Keycloak with OIDC and TOTP; optional LDAP federation | JWT validation, MFA support, RBAC | `security/keycloak/realm-export.json`, `backend/app/core/security.py` | enforce role policy and TOTP rollout | `/api/v1/auth/me`, route protection | LDAP federation remains site-specific |
| Password safety | delegated to IdP | Keycloak password storage | `docs/security.md` | password policy in Keycloak | admin review | Depends on IdP hardening |
| 2FA on-prem | Keycloak OTP | TOTP policy in realm | `security/keycloak/realm-export.json` | required action for staff users | login walkthrough | user enrollment still operational task |
| RBAC | route-level dependency checks | role gates | `backend/app/api/routes/*.py` | role governance | API behavior | mis-assignment of roles by admin |
| Data in transit | Caddy HTTPS | internal PKI | `infra/caddy/Caddyfile` | trust/distribute internal CA | smoke test over HTTPS | enterprise trust rollout |
| Sensitive data at rest | field encryption + encrypted docs | Fernet encryption | `backend/app/core/encryption.py`, `backend/app/storage/local_fs.py` | key custody | code inspection | host-level full disk encryption still external |
| No hardcoded secrets | env / `_FILE` support | config loader | `backend/app/core/config.py`, `.env.example` | secret bootstrap script | deployment review | `.env` file protection is operator responsibility |
| Failure resilience | circuit breaker, retry budget, bulkheads | auth fetch protections | `backend/app/core/circuit_breaker.py`, `retry.py`, `bulkhead.py` | readiness alerts | code inspection | other dependencies are still single-instance |
| Retry storm prevention | retry budget | bounded retries | `backend/app/core/retry.py` | monitor errors | code inspection | not global across all services |
| Health checks | live / ready / startup | public endpoints | `backend/app/api/routes/health.py` | smoke test, container health | health endpoints | metrics unauthenticated unless network-restricted |
| Logging rotation | rotating file handlers + docker log caps | structured logs | `backend/app/core/logging.py`, `docker-compose.yml` | disk monitoring | runtime logs | audit volume still needs retention review |
| Audit logging | DB + file audit | security-sensitive events | `backend/app/services/audit_service.py` | audit review | `/api/v1/admin/audit` | admin access must be restricted |
| DB size management | retention cleanup, keep blobs off DB | cleanup job | `backend/app/services/maintenance_service.py`, `docs/operations/maintenance.md` | scheduled cleanup | task logs | no partitioning included |
| Automated backups | Celery beat backup task | logical backup bundles | `backend/app/tasks/backups.py`, `services/backup_service.py` | nightly schedule | backup directory evidence | single-host storage unless externalized |
| Backup validation | checksum + `pg_restore --list` | validation task and script | `services/backup_service.py`, `scripts/validate_backup.ps1` | weekly validation | validation output | does not restore into isolated test DB automatically |
| Restore verification | explicit restore script + runbook | restore workflow | `scripts/restore_db.ps1`, `docs/operations/backup-restore.md` | DR drill | smoke test post-restore | operator error remains possible |
| Migration strategy | Alembic managed schema | versioned migration | `backend/alembic/*` | pre-deploy migration run | migration command | no automatic downgrade logic beyond script |
| Windows deployment | PowerShell first | deploy, rollback, smoke test | `scripts/deploy_windows.ps1`, `rollback_windows.ps1`, `healthcheck_smoke_test.ps1` | prerequisite checks | script output | host-specific Docker issues |
| Folder documentation | README in every folder | generated folder docs | `create_project.py` generated READMEs | documentation review | repository tree | content quality depends on metadata maintenance |
