# Integration Helpers

This folder helps load the dummy-data pack into the **current Municipal Licensing & Property Platform API**.

## Files

- `import_via_api.py`
  - imports properties and licenses through the current API
  - resolves property numbers to created property IDs
  - replays workflow transitions from the seed plan
  - uploads sample text documents to license records

- `current_schema_field_mapping.md`
  - explains how exported fields map to the current API

## Prerequisites
- Python 3.10+
- `requests` library
- reachable application base URL
- valid bearer token for a user with:
  - property create rights
  - licensing create/transition rights
  - document upload rights

## Basic usage

```bash
python import_via_api.py \
  --base-url http://localhost:8080 \
  --token <BEARER_TOKEN> \
  --profile-dir ../exports/developer_seed
```

## What the importer does

1. reads `properties_api.jsonl`
2. POSTs each property to `/api/v1/properties`
3. stores created property IDs by `property_number`
4. reads `licenses_api_plan.jsonl`
5. POSTs each license to `/api/v1/licenses`
6. replays transition paths such as:
   - submit
   - review
   - approve
   - reject
7. uploads matching files from `sample_documents/` to the created license record

## Idempotency
The importer sends a deterministic `Idempotency-Key` for property and license create operations so reruns are safer.

## Limitations
- this helper currently uploads seed documents to license records only
- it assumes the backend routes and auth contract from the generated repository
- it is intended for dev/UAT/demo seeding, not production bulk data migration

## Recommended usage pattern
- import `developer_seed` for developer work
- import `hybrid_demo` for demos and UAT
