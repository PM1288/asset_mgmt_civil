# Security Design

## Authentication model

- The frontend authenticates users with Keycloak using standard browser-based OIDC with PKCE over the same Caddy-served HTTPS host.
- The backend validates JWT bearer tokens offline using the realm JWKS endpoint.
- JWT signing keys are cached locally to reduce dependency on live auth availability.
- Auth key refresh is protected by a retry budget, bulkhead, and circuit breaker.

## Authorization model

Realm roles:
- `municipal-admin`
- `property-officer`
- `licensing-officer`
- `auditor`
- `viewer`
- `operator`

Authorization is enforced in the API layer through route dependencies. There is no implicit privilege escalation inside service code.

## Password and MFA handling

- Password storage is delegated to Keycloak, which provides industry-standard password hashing and policy controls.
- TOTP is supported through Keycloak and should be made mandatory for privileged users.
- The included realm template enables OTP policy settings; operational rollout should set required actions or flows for staff groups.

## LDAP and directory integration

Default deployment uses Keycloak’s internal user store. This is acceptable for small or isolated on-premises deployments.

For enterprises with AD/LDAP:
- use Keycloak user federation to bind to an internal directory,
- map directory groups to the included realm roles,
- keep TOTP enabled at Keycloak or directory-layer MFA if organizational policy requires it.

A sample LDIF is included under `security/ldap/` for lab use only.

## Session and token controls

- Short access token lifetime.
- Session idle and max lifespan settings in the realm template.
- Stateless API with bearer token validation.
- No server-side application session store is required beyond Keycloak session management.

## Data protection

### In transit
- Caddy terminates HTTPS using an internal CA by default.
- Internal Docker traffic is isolated on the compose network.
- Production deployments can replace internal TLS with enterprise-issued certificates if required.

### At rest
- Database-level at-rest encryption is expected from the host and storage platform.
- Application-layer encryption is implemented for sensitive fields such as owner/applicant contacts and remarks.
- Uploaded documents are encrypted before writing to the mounted document volume.
- Backups contain encrypted documents plus a logical database dump.

## Logging and audit

- Structured application logs are emitted in JSON.
- Audit events are stored in the database and mirrored to a dedicated audit log file.
- Docker logging options cap per-container log growth.
- Audit coverage includes creation, update, workflow transition, document upload, and maintenance actions.

## Brute-force and abuse controls

- Keycloak brute-force protection is enabled in the included realm import.
- API-level request throttling is applied using Redis with local-memory fallback.
- Idempotency support reduces duplicate mutations caused by retries and client uncertainty.

## Secret management

- Secrets are not committed.
- `.env.example` contains only placeholders.
- Runtime secrets are expected via `.env`, environment injection, or `_FILE`-style inputs.
- The generator includes a PowerShell secret bootstrap script.

## Administrative hardening guidance

- Restrict `/metrics` and Keycloak admin access at the network layer.
- Replace default passwords immediately.
- Make TOTP mandatory for privileged roles.
- Disable public API docs in production after commissioning if policy requires it.
- Backup the Keycloak database and application database separately.
- Monitor certificate lifetime if you replace the internal CA with enterprise certificates.

## Threat considerations

| Threat | Mitigation |
|---|---|
| Token forgery | Offline JWT verification using realm signing keys |
| Replay / duplicate submit | Idempotency keys on unsafe create operations |
| Brute force | Keycloak brute-force protection + API rate limiting |
| Data leakage at rest | Field encryption + encrypted document storage |
| Log exhaustion | Rotating file handlers + Docker log caps |
| Dependency flapping | Retry budget + circuit breaker + readiness endpoints |
| Silent backup corruption | Checksum manifest + validation using `pg_restore --list` |
