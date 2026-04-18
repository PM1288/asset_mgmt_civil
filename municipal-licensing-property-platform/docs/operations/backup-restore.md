# Backup and Restore

## Backup design

Backups are application-managed logical bundles containing:
- PostgreSQL logical dump in custom format (`pg_dump -Fc`)
- encrypted document volume archive (`tar.gz`)
- manifest with checksums and metadata

## Backup cadence

- Automated nightly backup through Celery Beat.
- Manual trigger through `scripts/backup_db.ps1` or admin endpoint.

## Validation

Validation checks:
1. manifest presence,
2. SHA-256 checksum of dump and document archive,
3. `pg_restore --list` for structural validation,
4. archive member inspection for the document tarball.

Use:
- `scripts/validate_backup.ps1 -BackupDir <path>`

## Restore workflow

1. Stop write services: API, worker, beat.
2. Restore database dump using `pg_restore`.
3. Replace encrypted document volume with the archived bundle.
4. Start services.
5. Run smoke tests.

Use:
- `scripts/restore_db.ps1 -BackupDir <path>`

## Recovery objectives

Planning defaults for this reference implementation:
- RPO: approximately 24 hours under the scheduled nightly backup policy
- RTO: 1 to 4 hours depending on database size, document volume size, and operator readiness

Municipal production environments should tune these values according to statutory and operational obligations.
