param(
    [string]$EnvFilePath = ".env"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot/helpers.ps1"

Write-Info "Triggering application-managed backup."
@'
import json
from app.services.backup_service import backup_service
print(json.dumps(backup_service.create_backup_bundle(), indent=2))
'@ | docker compose --env-file $EnvFilePath exec -T api python -
