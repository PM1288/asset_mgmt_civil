# Municipal Licensing & Property Platform — Dummy Data Pack

## What this package is

This package contains **synthetic but operationally realistic** seed data for the Municipal Licensing & Property Platform.

It is designed for three use cases:

1. **developer seeding**
   - small enough for quick local testing

2. **demo / UAT seeding**
   - richer data mix for realistic screens and dashboards

3. **future-schema exploration**
   - richer v2 CSVs that go beyond the current repository schema without breaking the current MVP

---

## What is real vs synthetic

### Real / publicly anchored
These elements are grounded in official public material:
- Mumbai ward office names and many office addresses
- Pune ward office names and area patterns
- Mumbai budget reference metrics for property tax and licence-department revenue
- Pune public revenue lines for property tax & water tax
- public PMC AutoDCR field patterns such as survey/CTS/plot/participant roles
- C-DAC product context for ERP / WAMIS / e-auth / e-sign positioning

### Synthetic
These are generated and safe:
- individual properties
- owners/applicants
- contacts
- applications
- workflow events
- audit events
- sample documents
- user accounts
- synthetic operational KPIs

No real citizen or applicant data is included.

---

## Profiles included

## 1. `developer_seed`
A compact profile for local development and smoke testing.

Use when you want:
- fast imports
- light tables
- easy debugging
- representative but small data

## 2. `hybrid_demo`
A medium-sized profile for demos, UX validation, UAT, and workflow testing.

Use when you want:
- more ward spread
- more status variety
- better dashboard realism
- fuller document and workflow history

---

## Package structure

- `exports/`
  - current-schema compatible payloads and lookup files

- `generator/`
  - the generator script and metadata catalogs

- `integration/`
  - helper script(s) and field mappings for importing into the current API

- `recommended_extension_model/`
  - richer v2 CSVs for future schema work

---

## Current-schema files

Each profile under `exports/` includes:

- `properties_api.jsonl`
  - one JSON object per property, ready for current property-create API logic

- `licenses_api_plan.jsonl`
  - one JSON object per license application with target status and transition path

- `ward_metadata.csv`
  - ward code, ward name, areas, postal codes, zone, center coordinates, and office address where available

- `user_profiles.csv`
  - synthetic users and role assignments

- `keycloak_users_seed.json`
  - seedable user metadata for identity setup / test harnessing

- `dashboard_metrics.json`
  - separates **public reference metrics** from **synthetic operational metrics**

- `workflow_events.csv`
  - generated workflow timeline events for demo or v2 seeding

- `audit_events.csv`
  - generated audit events for demo or v2 seeding

- `sample_documents/`
  - text attachments mapped by application number

- `import_manifest.json`
  - profile-level summary, counts, and generated-at metadata

---

## Recommended extension model files

Each profile under `recommended_extension_model/` includes:

- `properties_v2.csv`
- `licenses_v2.csv`
- `inspections_v2.csv`
- `payments_v2.csv`
- `documents_v2_manifest.csv`

These are **not required by the current backend**. They are the recommended next-step model for richer municipal UX and workflow realism.

---

## When to use which files

### Use `exports/*` when:
- loading the current repository
- testing existing APIs
- validating lists, filters, and status views
- demonstrating current MVP behavior

### Use `recommended_extension_model/*` when:
- planning schema v2
- building richer property detail pages
- adding payment, inspection, or participant roles
- designing more advanced license workflows

---

## How to generate new data

From the `generator/` directory:

```bash
python generate_dummy_data.py --profile developer_seed --output-dir ./out
python generate_dummy_data.py --profile hybrid_demo --output-dir ./out
```

---

## How to import into the current application

Use the helper in `integration/import_via_api.py`.

High-level process:
1. create/import properties from `properties_api.jsonl`
2. create license applications from `licenses_api_plan.jsonl`
3. resolve property numbers to created property IDs
4. move applications through transition paths
5. upload sample text documents to license records

See `integration/README.md` for usage.

---

## Design notes

### Why license seed records store `property_number` instead of `property_id`
The seed pack is application-portable. The importer resolves the created property ID at runtime so the same dataset can be loaded into a fresh environment.

### Why operational KPI numbers are synthetic
The application should never pretend that generated case counts are official municipal throughput. Therefore:
- official numbers are labeled as **public reference metrics**
- app-case counts are labeled as **synthetic operational metrics**

### Why documents are plain text in this pack
The current backend explicitly supports `text/plain`, and text files keep the data pack lightweight, reviewable, and easy to import. These are sufficient for UI, storage, audit, and upload-path validation.

---

## Recommended import sequence for demos

### For quick local development
Use:
- `exports/developer_seed/`

### For stakeholder walkthroughs
Use:
- `exports/hybrid_demo/`
- `recommended_extension_model/hybrid_demo/` as a companion for future-state conversations

---

## Safety and privacy

This data pack is intended for:
- local development
- UAT
- training
- demo environments

It is not intended for:
- production analytics
- legal correspondence
- real taxpayer or applicant handling

---

## Reference anchors
See:
- `SOURCES_AND_METHOD.md`
- `integration/README.md`
- `recommended_extension_model/README.md`
