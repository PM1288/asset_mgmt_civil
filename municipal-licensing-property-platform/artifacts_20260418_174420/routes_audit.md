# Routes and Screens Audit

## 1. Keycloak Login

- Route/path: `/` while unauthenticated, redirecting into the Keycloak login flow under `/auth/...`
- Screen name: Keycloak login
- Discovery: Accessible
- How reached: Opened the base URL in a fresh browser context without a session
- What it does: Prompts for username and password before the SPA loads
- Notable UI elements: Username field, password field, sign-in button, Keycloak-branded login layout
- Desktop screenshot: `screenshots/desktop-login.png`
- Mobile screenshot: `screenshots/mobile-login.png`

## 2. Dashboard

- Route/path: `/` with internal `dashboard` tab state
- Screen name: Dashboard
- Discovery: Accessible
- How reached: Logged in as an admin user and landed on the default tab
- What it does: Shows a summary of the authenticated user, roles, deployment model, and auth model
- Notable UI elements: Sidebar navigation, username display, four metric cards, `Dashboard` heading
- Desktop screenshot: `screenshots/desktop-dashboard.png`
- Mobile screenshot: `screenshots/mobile-dashboard.png`

## 3. Properties

- Route/path: `/` with internal `properties` tab state
- Screen name: Properties
- Discovery: Accessible
- How reached: Clicked `PROPERTIES` in the sidebar after login
- What it does: Allows creation of property records and lists existing properties
- Notable UI elements: Multi-field property form, `Create Property` button, properties table with number/ward/address/status/owner columns
- Desktop screenshot: `screenshots/desktop-properties.png`
- Mobile screenshot: `screenshots/mobile-properties.png`

## 4. Licenses

- Route/path: `/` with internal `licenses` tab state
- Screen name: Licenses
- Discovery: Accessible
- How reached: Clicked `LICENSES` in the sidebar after login
- What it does: Allows creation of license applications and lists existing licenses
- Notable UI elements: License form, `Create License` button, licenses table with application/property/type/status/applicant columns
- Desktop screenshot: `screenshots/desktop-licenses.png`
- Mobile screenshot: `screenshots/mobile-licenses.png`

## 5. Health

- Route/path: `/` with internal `health` tab state
- Screen name: Health
- Discovery: Accessible
- How reached: Clicked `HEALTH` in the sidebar after login
- What it does: Surfaces backend readiness information to the operator UI
- Notable UI elements: Health cards, component status indicators, dependency detail text
- Desktop screenshot: `screenshots/desktop-health.png`
- Mobile screenshot: `screenshots/mobile-health.png`

## 6. Admin Diagnostics

- Route/path: `/` with internal `admin` tab state
- Screen name: Admin diagnostics
- Discovery: Accessible
- How reached: Clicked `ADMIN` in the sidebar while logged in as an admin user
- What it does: Shows dependency readiness, disk usage, and configured limits from the backend diagnostics endpoint
- Notable UI elements: `Diagnostics` heading, JSON diagnostics payload, sidebar navigation
- Desktop screenshot: `screenshots/desktop-admin-diagnostics.png`
- Mobile screenshot: `screenshots/mobile-admin-diagnostics.png`

## 7. Admin Diagnostics Denied State

- Route/path: `/` with internal `admin` tab state
- Screen name: Admin diagnostics denied
- Discovery: Accessible with restriction
- How reached: Logged in as a viewer user, clicked `ADMIN`, and observed the role-based denial state
- What it does: Demonstrates access control for the protected admin diagnostics screen
- Notable UI elements: Error box with authorization failure, unchanged app shell/sidebar
- Desktop screenshot: `screenshots/desktop-admin-denied.png`
- Mobile screenshot: `screenshots/mobile-admin-denied.png`

## 8. Swagger API Docs

- Route/path: `/docs`
- Screen name: Swagger API docs
- Discovery: Accessible
- How reached: Direct navigation discovered from proxy and FastAPI code
- What it does: Exposes interactive API documentation for backend routes
- Notable UI elements: Swagger UI shell, operation groups, endpoint list, API explorer controls
- Desktop screenshot: `screenshots/desktop-api-docs.png`
- Mobile screenshot: `screenshots/mobile-api-docs.png`

## 9. Workflow History API

- Route/path: `/api/v1/workflows/{aggregate_type}/{aggregate_id}`
- Screen name: Workflow history endpoint
- Discovery: Only discovered in code
- How reached: Found in `backend/app/api/routes/workflows.py` and router composition in `backend/app/api/router.py`
- What it does: Returns workflow history events for an aggregate
- Notable UI elements: No dedicated browser screen; API-only capability
- Desktop screenshot: `N/A`
- Mobile screenshot: `N/A`

## 10. Document Download API

- Route/path: `/api/v1/documents/{document_id}/download`
- Screen name: Document download endpoint
- Discovery: Only discovered in code
- How reached: Found in `backend/app/api/routes/documents.py`
- What it does: Streams encrypted document payloads back to authorized users
- Notable UI elements: No dedicated browser screen; download-only endpoint
- Desktop screenshot: `N/A`
- Mobile screenshot: `N/A`

## 11. Admin Audit and Backup APIs

- Route/path: `/api/v1/admin/audit`, `/api/v1/admin/backups/run`, `/api/v1/admin/backups/validate-latest`, `/api/v1/admin/maintenance/cleanup`
- Screen name: Admin operational endpoints
- Discovery: Only discovered in code
- How reached: Found in `backend/app/api/routes/admin.py`
- What it does: Exposes admin-only audit retrieval and operational actions such as backup and cleanup
- Notable UI elements: No dedicated browser screen in the shipped frontend; these are backend operational endpoints
- Desktop screenshot: `N/A`
- Mobile screenshot: `N/A`

## Summary

- User-visible SPA screens discovered: 5 primary tabs on `/`
- Additional browser-accessible non-SPA screens discovered: 2
  - Keycloak login
  - Swagger API docs
- Backend route families discovered without dedicated frontend screens: 3 notable groups documented above
