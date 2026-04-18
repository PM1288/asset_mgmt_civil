# Current Schema Field Mapping

## Property import mapping

Source file: `exports/<profile>/properties_api.jsonl`  
Target endpoint: `POST /api/v1/properties`

| Source field | Target field | Notes |
|---|---|---|
| `property_number` | `property_number` | Unique business key |
| `ward_code` | `ward_code` | Ward-scoped routing |
| `address_line_1` | `address_line_1` | Required |
| `address_line_2` | `address_line_2` | Optional |
| `city` | `city` | Usually Pune or Mumbai |
| `district` | `district` | Usually Pune or Mumbai |
| `state` | `state` | Maharashtra |
| `postal_code` | `postal_code` | Optional but realistic |
| `geo_lat` | `geo_lat` | Optional |
| `geo_lng` | `geo_lng` | Optional |
| `status` | `status` | e.g. active, under_verification |
| `use_type` | `use_type` | e.g. residential, commercial |
| `owner_name` | `owner_name` | Backend encrypts at rest |
| `owner_contact` | `owner_contact` | Backend encrypts at rest |
| `assessment_zone` | `assessment_zone` | Optional |
| `remarks` | `remarks` | Optional municipal note |

## License import mapping

Source file: `exports/<profile>/licenses_api_plan.jsonl`  
Primary target endpoint: `POST /api/v1/licenses`

| Source field | Target field | Notes |
|---|---|---|
| `application_number` | `application_number` | Unique business key |
| `property_number` | resolved to `property_id` | Importer maps created property IDs |
| `license_type` | `license_type` | Current enum is open string |
| `applicant_name` | `applicant_name` | Backend encrypts at rest |
| `applicant_contact` | `applicant_contact` | Backend encrypts at rest |
| `notes` | `notes` | Initial remarks |

## Transition replay mapping

The importer uses `transition_path` to call:

| Transition token | Endpoint |
|---|---|
| `submit` | `POST /api/v1/licenses/{license_id}/submit` |
| `review` | `POST /api/v1/licenses/{license_id}/review` |
| `approve` | `POST /api/v1/licenses/{license_id}/approve` |
| `reject` | `POST /api/v1/licenses/{license_id}/reject` |

Payload shape for transition endpoints:
```json
{
  "comments": "seed comment",
  "assignee": "username"
}
```

## Document upload mapping

Source directory: `exports/<profile>/sample_documents/`  
Target endpoint: `POST /api/v1/licenses/{license_id}/documents`

Current seed attachments are plain-text files and should be sent as:
- content type: `text/plain`

Filename convention:
- `<application_number>_application_note_01.txt`
- `<application_number>_ownership_note_02.txt`
- `<application_number>_site_photo_note_03.txt`
- `<application_number>_deficiency_memo_04.txt`

## Notes
- the current backend supports only the current schema; richer v2 files are intentionally separate
- create payloads use idempotency keys for safer reruns
