# Maintenance

## Automated maintenance

The scheduler executes:
- retention cleanup,
- nightly backup,
- weekly backup validation.

## Manual maintenance scripts

- `scripts/cleanup_db.ps1`
- `scripts/run_migrations.ps1`
- `scripts/backup_db.ps1`
- `scripts/validate_backup.ps1`

## Database growth controls

- Audit and idempotency retention are bounded.
- Temporary idempotency data is pruned.
- Document payloads are kept out of the database and stored encrypted on disk.
- Additional archival can be layered above the included retention policy.

## Long-term care

- Reindexing, vacuum tuning, and storage growth monitoring remain DBA responsibilities.
- The application’s schema is migration-managed; do not patch tables ad hoc.
- Keep backup validation evidence for audit purposes.
