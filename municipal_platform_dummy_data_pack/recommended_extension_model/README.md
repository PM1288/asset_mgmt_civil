# Recommended Extension Model

This folder contains a **future-state municipal data model** that goes beyond the current repository schema.

Use it when:
- planning schema v2
- designing richer UI/UX
- adding payment, inspection, or participant-role handling
- aligning the platform more closely to real municipal licensing/property practice

## Files

### `properties_v2.csv`
Recommended future property fields:
- survey_no
- hissa_no
- cts_no / cs_no
- plot_no
- final_plot_no
- locality
- land_area_sq_m
- built_up_area_sq_m
- rateable_value
- estimated_annual_property_tax
- occupancy_class
- ownership_type

### `licenses_v2.csv`
Recommended future license/application fields:
- filing_channel
- target_sla_days
- fee_amount
- payment_status
- deficiency_count
- architect_name
- developer_name
- structural_engineer_name
- business_name
- order_reference
- signed_order_attached

### `inspections_v2.csv`
Future inspection events:
- inspection type
- scheduled date
- inspected date
- inspector
- outcome
- deficiency summary

### `payments_v2.csv`
Future fee/payment records:
- demand number
- amount demanded
- amount paid
- payment reference
- payment date
- status

### `documents_v2_manifest.csv`
Suggested document taxonomy and linkage

## Compatibility note
These files are **not required** by the current backend. They are a design and implementation aid for the next evolution of the platform.
