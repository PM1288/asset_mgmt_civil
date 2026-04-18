# Generator

This folder contains the seed-data generator and its static catalogs.

## Files

- `generate_dummy_data.py`
  - builds synthetic but realistic datasets for one named profile

- `municipal_seed_catalog.json`
  - ward definitions, city anchors, public reference metrics, and shared enumerations

- `municipal_seed_profiles.json`
  - profile definitions such as record counts and output mix

## Usage

```bash
python generate_dummy_data.py --profile developer_seed --output-dir ./out
python generate_dummy_data.py --profile hybrid_demo --output-dir ./out
```

## Output contract
The generator creates:
- current-schema export files
- recommended v2 CSVs
- sample attachments
- import manifests

## Notes
- data is synthetic
- ward metadata and public reference metrics are anchored to official public sources
- individual persons and properties are fictional
