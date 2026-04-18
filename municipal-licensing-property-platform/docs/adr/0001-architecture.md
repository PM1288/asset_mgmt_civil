# ADR 0001 - Stack Selection

## Status
Accepted

## Decision
Use:
- FastAPI backend
- PostgreSQL primary store
- Redis for rate limiting and worker broker/backend
- Celery worker and beat for asynchronous jobs
- Keycloak for identity, TOTP, and optional LDAP federation
- React/Vite frontend
- Caddy reverse proxy with internal TLS
- Docker Compose for deployment on a Windows host

## Rationale
The stack is mature, operationally familiar, self-hostable, and compatible with brownfield municipal environments.

## Consequences
- Compose is simpler than Kubernetes for the target scope but does not provide multi-host orchestration.
- Keycloak adds another database and service but greatly simplifies MFA, RBAC, and federation.
- Caddy reduces TLS bootstrap friction relative to Nginx in local and lab environments.
