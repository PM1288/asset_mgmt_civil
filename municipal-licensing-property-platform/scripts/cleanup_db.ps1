param(
    [string]$EnvFilePath = ".env"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot/helpers.ps1"

Write-Info "Running retention cleanup through the scheduler task."
@'
from app.db.session import SessionLocal
from app.services.maintenance_service import maintenance_service

db = SessionLocal()
try:
    result = maintenance_service.cleanup(db, actor="manual-cleanup", ip_address=None)
    db.commit()
    print(result)
finally:
    db.close()
'@ | docker compose --env-file $EnvFilePath exec -T api python -
