# Disaster Recovery

## Failure domains

- App DB
- Keycloak DB
- Redis
- Caddy / edge
- API / worker containers
- Document and backup volumes
- Windows host

## DR strategy

- Use separate named volumes for databases.
- Keep backup bundles on a host path that is itself protected by the municipal backup policy.
- Back up the application DB and Keycloak DB independently.
- Treat the encrypted document volume as first-class recoverable data.

## Recommended DR exercise

1. Restore backup into a clean environment.
2. Rebuild images from the repository.
3. Run migrations.
4. Restore the latest validated backup.
5. Verify logins, property listing, license listing, document download, and health endpoints.
6. Record elapsed recovery time and remediation steps.

## Non-goals

This reference stack does not implement synchronous cross-site replication or active-active failover. Those patterns belong to a larger HA program and can be layered later.
