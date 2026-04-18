# Boundary Condition Analysis

## Frontend ↔ Backend
- **Normal assumptions:** same origin through Caddy; bearer token present.
- **Contract:** JSON over HTTPS; API prefix `/api/v1`.
- **Timeout/retry:** browser default, no blind mutation retries without idempotency.
- **Failure scenarios:** API 5xx, auth expiry, CORS mismatch.
- **Blast radius:** user session only unless systemic.
- **Detection:** browser errors, Caddy logs, API metrics.
- **Containment:** static frontend remains available; mutations require explicit retries.
- **Degraded mode:** dashboard may load partially if some endpoints fail.
- **Restoration:** refresh token, redeploy API, fix proxy config.
- **Operator notes:** confirm `APP_HOSTNAME`, Caddy routes, and frontend base path.

## Backend ↔ Auth / IdP
- **Normal assumptions:** Keycloak reachable on Docker network; JWKS endpoint available.
- **Contract:** OIDC issuer metadata and JWT signatures.
- **Timeout/retry:** bounded retries with jitter and retry budget.
- **Failure scenarios:** key fetch outage, invalid realm config, signing key change.
- **Blast radius:** new token validation may fail once cache expires.
- **Detection:** auth component unhealthy in readiness.
- **Containment:** JWKS cache plus circuit breaker avoids retry storms.
- **Degraded mode:** existing cached-key validation continues for a limited period.
- **Restoration:** restore Keycloak service, verify realm, refresh client settings.
- **Operator notes:** keep a break-glass admin account and realm export.

## Backend ↔ 2FA subsystem
- **Normal assumptions:** TOTP configured in Keycloak for privileged users.
- **Contract:** MFA completed before tokens are issued.
- **Timeout/retry:** handled by Keycloak.
- **Failure scenarios:** TOTP misconfiguration, user device loss.
- **Blast radius:** affected user or group.
- **Detection:** login support incidents.
- **Containment:** admin reset via Keycloak.
- **Degraded mode:** none for affected user until reset.
- **Restoration:** reset required action or device binding.
- **Operator notes:** document recovery procedure for lost authenticators.

## Backend ↔ Database
- **Normal assumptions:** low-latency local network, healthy connection pool.
- **Contract:** transactional SQL operations and alembic-managed schema.
- **Timeout/retry:** no automatic transaction replay; failures surface quickly.
- **Failure scenarios:** outage, schema drift, deadlocks, storage full.
- **Blast radius:** broad platform impact.
- **Detection:** readiness failure, SQL exceptions, migration errors.
- **Containment:** request failure rather than silent inconsistency.
- **Degraded mode:** none for write paths; read paths also fail if DB unavailable.
- **Restoration:** restore DB, run migrations, validate health.
- **Operator notes:** never hot-edit schema outside migrations.

## Backend ↔ Cache / Redis
- **Normal assumptions:** Redis available for throttling and Celery.
- **Contract:** INCR/TTL for rate limiting; broker/backend for Celery.
- **Timeout/retry:** short socket timeouts; fallback to memory for throttle.
- **Failure scenarios:** Redis crash, high memory, AOF corruption.
- **Blast radius:** async tasks pause; throttling becomes local only.
- **Detection:** readiness degraded, worker errors.
- **Containment:** local fallback for throttling; API continues.
- **Degraded mode:** delayed maintenance and backup schedules.
- **Restoration:** restore Redis, observe backlog drain.
- **Operator notes:** inspect queue depth after recovery.

## Backend ↔ Job scheduler / worker
- **Normal assumptions:** beat schedules tasks and worker consumes them.
- **Contract:** Celery task payloads over Redis.
- **Timeout/retry:** task-level soft/hard limits; no infinite replay loops.
- **Failure scenarios:** beat down, worker down, poison task.
- **Blast radius:** maintenance and backup lag.
- **Detection:** missing backups, stale cleanup, queue age.
- **Containment:** foreground API isolated from worker process.
- **Degraded mode:** platform usable but operational debt accumulates.
- **Restoration:** restart worker/beat, inspect failed task history.
- **Operator notes:** backlog is a warning, not just a nuisance.

## Backend ↔ File storage
- **Normal assumptions:** mounted local volume with sufficient free space.
- **Contract:** encrypted file read/write via relative path metadata.
- **Timeout/retry:** no aggressive retry; storage bulkhead limits concurrency.
- **Failure scenarios:** disk full, permission loss, archive corruption.
- **Blast radius:** upload/download only, metadata remains in DB.
- **Detection:** diagnostics disk stats, upload failures.
- **Containment:** document service failure does not corrupt DB transaction if handled correctly.
- **Degraded mode:** case processing without new attachments.
- **Restoration:** free disk, repair permissions, restore documents.
- **Operator notes:** document volume is recoverable data and must be backed up.

## Reverse proxy ↔ App containers
- **Normal assumptions:** internal DNS names stable, health checks pass.
- **Contract:** HTTP proxy upstreams.
- **Timeout/retry:** proxy transport timeouts configured; no unbounded retries.
- **Failure scenarios:** upstream unavailable, wrong port, bad route.
- **Blast radius:** edge outage or partial path outage.
- **Detection:** user-visible errors, smoke tests.
- **Containment:** simple routing limits complexity.
- **Degraded mode:** static or API path may fail independently.
- **Restoration:** fix compose service or Caddyfile and redeploy.
- **Operator notes:** validate both `/` and `/health/*` after changes.

## App ↔ Docker network
- **Normal assumptions:** Compose network healthy and isolated.
- **Contract:** service DNS names resolve inside network.
- **Timeout/retry:** short network timeouts at app layer.
- **Failure scenarios:** DNS failure, bridge issue, host firewall interference.
- **Blast radius:** multi-service impairment.
- **Detection:** cross-service health failures.
- **Containment:** retries are budgeted; not all calls retry forever.
- **Degraded mode:** whichever cached/fallback paths exist continue briefly.
- **Restoration:** repair Docker networking and restart affected services.
- **Operator notes:** check Windows host virtualization health.

## Backup subsystem ↔ Storage target
- **Normal assumptions:** backup path writable and persistent.
- **Contract:** file-system writes with checksum manifest.
- **Timeout/retry:** task-level retry through scheduler, no infinite retry storm.
- **Failure scenarios:** path unavailable, partial write, disk full.
- **Blast radius:** future recovery risk, not immediate user outage.
- **Detection:** missing bundle, validation failure.
- **Containment:** keep previous validated bundles.
- **Degraded mode:** application still runs.
- **Restoration:** repair storage, run manual backup, validate immediately.
- **Operator notes:** monitor both capacity and validation status.

## Logging subsystem ↔ Filesystem / disk
- **Normal assumptions:** log path writable; rotation active.
- **Contract:** structured JSON lines.
- **Timeout/retry:** synchronous local writes; rotation caps growth.
- **Failure scenarios:** disk full, permission failure.
- **Blast radius:** possible process instability if unhandled.
- **Detection:** disk stats, missing log files.
- **Containment:** Docker log caps and file rotation.
- **Degraded mode:** reduced observability.
- **Restoration:** free space, restore path permissions.
- **Operator notes:** do not mount logs to ephemeral paths you expect to audit later.

## Deployment scripts ↔ Windows host
- **Normal assumptions:** Git, Docker, PowerShell available.
- **Contract:** scripts call compose, git, tar, and web checks.
- **Timeout/retry:** human-driven orchestration with explicit waits.
- **Failure scenarios:** missing CLI tools, path permissions, antivirus interference.
- **Blast radius:** deploy or rollback blocked.
- **Detection:** script failure output.
- **Containment:** preflight command checks.
- **Degraded mode:** none; deployment pauses safely.
- **Restoration:** install prerequisites, rerun deploy.
- **Operator notes:** prefer PowerShell 7 and ensure Docker Desktop resources are sufficient.

## GitHub source ↔ Deployment pipeline
- **Normal assumptions:** repository reachable and working tree clean.
- **Contract:** clone/pull, build, tag, compose deploy.
- **Timeout/retry:** git pull is manual/explicit.
- **Failure scenarios:** bad commit, partial checkout, missing env.
- **Blast radius:** new release only.
- **Detection:** build failure, smoke test failure.
- **Containment:** previous release tag retained locally for rollback.
- **Degraded mode:** current production keeps running until new images start.
- **Restoration:** rollback to previous tag or redeploy fixed commit.
- **Operator notes:** do not delete prior images until the new release is verified.
