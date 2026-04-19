# Repository Overview

## What this app does

This repository contains a self-hosted municipal operations platform for property records and licensing workflows. It is designed for Windows-hosted Docker deployment and combines:

- a React/Vite frontend
- a FastAPI backend
- Keycloak for authentication
- PostgreSQL for data
- Redis/Celery for background work
- Caddy as the reverse proxy/TLS edge

The browser UI focuses on a small authenticated operator console with screens for dashboard metrics, property management, license management, health status, and admin diagnostics.

## Important folders and files

- `README.md`
  High-level product and deployment overview.
- `docker-compose.yml`
  Runtime topology and host exposure.
- `infra/caddy/Caddyfile`
  Reverse-proxy routing for frontend, backend, and Keycloak.
- `frontend/package.json`
  Frontend build tooling and scripts.
- `frontend/src/main.tsx`
  Frontend bootstrap; initializes Keycloak with `login-required`.
- `frontend/src/App.tsx`
  Main SPA shell; implements the visible screen switching.
- `frontend/src/pages/`
  Screen-level React components:
  - `DashboardPage.tsx`
  - `PropertiesPage.tsx`
  - `LicensesPage.tsx`
  - `HealthPage.tsx`
  - `AdminPage.tsx`
- `frontend/src/components/`
  Shared UI elements such as the shell layout, data tables, and health cards.
- `backend/app/main.py`
  FastAPI application entry point.
- `backend/app/api/router.py`
  Backend router composition.
- `backend/app/api/routes/`
  Backend route families for auth, properties, licenses, workflows, documents, admin, and health.
- `scripts/`
  Windows-oriented operational scripts for deploy, rollback, migrations, smoke checks, backup, restore, and validation.
- `runtime/ui-smoke-tools/`
  Existing Playwright-based smoke helper area; I reused this location for selector guidance during the audit.

## Routing structure

### Browser-facing routing

The app does **not** use React Router or file-based browser routing. Instead:

- `frontend/src/main.tsx` boots Keycloak with `onLoad: "login-required"`.
- after authentication, the SPA mounts at `/`
- `frontend/src/App.tsx` keeps a local `tab` state and swaps screens inside the same URL

That means the primary UI screens are internal tab states on the root route rather than unique browser paths:

- `/` -> Dashboard tab
- `/` -> Properties tab
- `/` -> Licenses tab
- `/` -> Health tab
- `/` -> Admin tab

### Proxy-exposed paths

From `infra/caddy/Caddyfile`:

- `/auth/*` -> Keycloak
- `/api/*`, `/health/*`, `/docs*`, `/openapi.json`, `/redoc*` -> FastAPI backend
- everything else -> frontend SPA

### Backend route families

From `backend/app/api/router.py` and `backend/app/api/routes/`:

- `/api/v1/auth`
- `/api/v1/properties`
- `/api/v1/licenses`
- `/api/v1/workflows`
- `/api/v1/documents`
- `/api/v1/admin`
- system routes:
  - `/health/live`
  - `/health/ready`
  - `/health/startup`
  - `/docs`

These backend routes support the UI, but only part of them are surfaced as actual browser screens.

## Assumptions and limitations

- This audit was performed against the locally running deployed stack at `https://localhost:8443`, not against a separate Vite dev server.
- The environment uses Caddy internal TLS, so browser automation had to ignore locally untrusted certificates.
- Because the frontend uses tab state instead of URL routing, multiple meaningful screens share the same browser path `/`.
- Some backend route families were discovered in code but have no dedicated frontend screen.
- The audit focuses on meaningful user-visible screens and direct browser-accessible pages, not every API endpoint.
- Role-sensitive behavior matters:
  - admin diagnostics renders for privileged users
  - the same tab shows an authorization error for lower-privilege users
