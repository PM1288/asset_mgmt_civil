# Architecture

## Purpose

This platform manages municipal property records, licensing workflows, encrypted documents, and audit trails in an on-premises environment. It is designed for municipalities that already have external systems such as ERP, GIS, payment gateways, or signature services and need a resilient workflow core that can be deployed locally.

## Context

```mermaid
flowchart LR
    Citizen[Citizen / Applicant]
    Officer[Municipal Officer]
    Auditor[Auditor / Supervisor]
    Portal[Municipal Platform]
    IdP[Keycloak / Optional LDAP]
    DB[(PostgreSQL)]
    Cache[(Redis)]
    Docs[(Encrypted Document Volume)]
    Jobs[Celery Worker / Beat]
    ERP[ERP / Finance / GIS / C-DAC / SAP / Other Systems]
    Backup[Backup Repository]

    Citizen --> Portal
    Officer --> Portal
    Auditor --> Portal
    Portal --> IdP
    Portal --> DB
    Portal --> Cache
    Portal --> Docs
    Portal --> Jobs
    Portal <--> ERP
    Jobs --> Backup
```

## Container view

```mermaid
flowchart TB
    subgraph Browser
        SPA[React SPA]
    end

    subgraph Edge
        Caddy[Caddy TLS Proxy]
    end

    subgraph AppTier
        API[FastAPI API]
        Worker[Celery Worker]
        Beat[Celery Beat]
        Keycloak[Keycloak]
    end

    subgraph DataTier
        AppDB[(PostgreSQL App DB)]
        KCDB[(PostgreSQL Keycloak DB)]
        Redis[(Redis)]
        Files[(Encrypted Documents / Backups / Logs)]
    end

    SPA --> Caddy
    Caddy --> API
    Caddy --> SPA
    API --> Keycloak
    API --> AppDB
    API --> Redis
    API --> Files
    Worker --> AppDB
    Worker --> Redis
    Worker --> Files
    Beat --> Redis
    Beat --> Files
    Keycloak --> KCDB
```

## Component view

```mermaid
flowchart LR
    API[FastAPI]
    Auth[OIDC / JWT Validation]
    Property[Property Service]
    License[License Service]
    Workflow[Workflow Service]
    Document[Encrypted Document Service]
    Audit[Audit Service]
    Health[Health / Diagnostics]
    Maint[Retention / Backup Service]
    DB[(PostgreSQL)]
    FS[(Encrypted Files)]
    Redis[(Redis)]

    API --> Auth
    API --> Property
    API --> License
    API --> Workflow
    API --> Document
    API --> Audit
    API --> Health
    API --> Maint
    Property --> DB
    License --> DB
    Workflow --> DB
    Audit --> DB
    Document --> DB
    Document --> FS
    Health --> DB
    Health --> Redis
    Maint --> DB
    Maint --> FS
```

## Deployment view

```mermaid
flowchart TB
    subgraph Windows Host
        Git[Git Working Copy]
        Compose[Docker Compose]
        Runtime[runtime/ volumes]
    end

    subgraph Docker Network
        Proxy[Caddy]
        Frontend[Nginx + React]
        API[FastAPI]
        Worker[Celery Worker]
        Beat[Celery Beat]
        Keycloak[Keycloak]
        DB[(App PostgreSQL)]
        KCDB[(Keycloak PostgreSQL)]
        Redis[(Redis)]
    end

    Git --> Compose
    Compose --> Proxy
    Compose --> Frontend
    Compose --> API
    Compose --> Worker
    Compose --> Beat
    Compose --> Keycloak
    Compose --> DB
    Compose --> KCDB
    Compose --> Redis
    Runtime --> API
    Runtime --> Worker
    Runtime --> Beat
```

## Design principles

1. **On-premises first:** all core functions run locally.
2. **Security by default:** TOTP-capable identity, encrypted storage, strict headers, RBAC, audit logs.
3. **Resilience by containment:** retries are budgeted, auth fetches use a circuit breaker, rate limits are bounded, queues are separated from request threads.
4. **Operational simplicity:** Docker Compose, PowerShell deployment, local TLS using Caddy internal PKI, file-based backups, and explicit runbooks.
5. **Brownfield compatibility:** the system is a workflow core and not an ERP replacement. It can coexist with SAP, GIS, C-DAC services, or other municipal back-office systems.
