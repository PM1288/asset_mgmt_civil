# Sources and Method

## 1. Purpose

This note explains how the dummy-data pack balances realism and safety.

The package uses:
- official public municipal references for context
- synthetic records for individuals, properties, applications, and workflows

---

## 2. Official public anchors used

## C-DAC context
Used to position likely integration points and future workflow fields:
- C-DAC NextGen ERP
- C-DAC WAMIS
- e-Pramaan
- e-Hastakshar

## Mumbai (MCGM) references
Used for:
- ward office codes / addresses
- public budget context for property-tax and licensing revenue

## Pune (PMC) references
Used for:
- ward names and ward-operational references
- public tax receipt context
- public AutoDCR field patterns such as survey no., CTS no., plot no., architect, developer, and structural engineer roles

---

## 3. Synthetic generation rules

### Property realism rules
- each property belongs to Pune or Mumbai
- each property belongs to a real-looking ward code and ward name
- address lines are built from plausible locality and road patterns
- postal codes are chosen from city/ward-appropriate sets
- use type affects area, fees, tax estimate, and likely license types
- comments/remarks look like municipal operational notes, not lorem ipsum

### License realism rules
- application numbers are city- and service-prefixed
- license types are drawn from likely municipal workflows:
  - trade license
  - health NOC
  - signboard permission
  - building-plan approval
  - occupancy certificate
  - storage NOC
  - fire referral
  - estate permission
- transition paths are internally consistent with the current backend workflow model

### User realism rules
- usernames reflect department/ward style
- roles map to the current application RBAC pattern
- viewer, auditor, licensing officer, and municipal admin users are all present

### Document realism rules
- document names are tied to application numbers
- document text reflects ownership notes, application notes, site-photo notes, or deficiency-like notes
- no scanned real documents are included

---

## 4. What the numbers mean

## Public reference metrics
These are grounded to published public numbers and are included only as context for:
- dashboards
- demos
- data-storytelling
- municipal plausibility

They should be shown in the UI as **reference context**, not as live system totals.

## Synthetic operational metrics
These are generated case counts intended to make the dashboard and inbox believable for testing and demos.

They should be labeled clearly as synthetic in any demo or documentation.

---

## 5. Why real people and real parcel data are not used

Municipal property and licensing datasets are highly sensitive because they can reveal:
- ownership
- location
- inspection outcomes
- commercial activity
- compliance or enforcement status

Therefore the pack uses realistic structure but not real citizen or parcel identity.

---

## 6. Files that contain source-linked context

- `exports/*/dashboard_metrics.json`
- `exports/*/ward_metadata.csv`
- `generator/municipal_seed_catalog.json`

---

## 7. Primary public references

- C-DAC NextGen ERP  
  https://www.cdac.in/index.aspx?id=service_details&serviceId=CDACNextGenERP

- C-DAC WAMIS  
  https://cdac.in/index.aspx?id=ev_corp_wamis

- e-Pramaan  
  https://cdac.in/index.aspx?id=st_egov_e-Pramaan_Info_120220

- e-Hastakshar  
  https://www.cdac.in/index.aspx?id=service_details&serviceId=e-Hastakshar%3AC-DAC%27sOn-lineDigitalSigningService

- MCGM ward office address PDF  
  https://portal.mcgm.gov.in/irj/go/km/docs/documents/HomePage%20Data/CFC/Address%20and%20E-mail%20ID%27s%20of%20Ward%20Assistant%20Commissioner%20%26%20CFC%28Modified%20File%29.pdf

- MCGM budget speech 2025-26  
  https://www.mcgm.gov.in/irj/go/km/docs/documents/MCGM%20Department%20List/Chief%20Accountant%20%28Finance%29/Budget/Budget%20Estimate%202025-2026/1-%20MC%27s%20Speech/BUDGET%20A%2CB%2CG/ENGLISH%20SPEECH.pdf

- PMC open-data accounts / schedules  
  https://opendata.pmc.gov.in/opendata/6f5d15dd-7fd3-4b53-8a01-f85a00848952.pdf

- PMC AutoDCR public portal  
  https://autodcr.pmc.gov.in/
