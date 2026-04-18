# Runtime Data

This directory is mounted into containers for mutable operational state. It is intentionally excluded from version control except for this README and per-folder placeholders.

Subdirectories:
- `backups/` for logical database dumps and encrypted document archives.
- `documents/` for encrypted uploaded attachments.
- `logs/` for application, worker, and scheduler logs.
- `app/` for local runtime state such as release markers.

Treat the contents as operational data. Include them in your host backup policy and monitor disk consumption.
