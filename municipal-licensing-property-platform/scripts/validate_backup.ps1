param(
    [string]$BackupDir,
    [string]$EnvFilePath = ".env"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot/helpers.ps1"

if (-not $BackupDir) {
    throw "BackupDir is required."
}

$containerBackupDir = if ($BackupDir -match '^/') {
    $BackupDir
} else {
    $resolved = Resolve-Path $BackupDir -ErrorAction Stop
    "/srv/backups/$([IO.Path]::GetFileName($resolved.Path))"
}

Write-Info "Validating backup bundle $BackupDir"
@"
import json
from app.services.backup_service import backup_service
print(json.dumps(backup_service.validate_backup_bundle(r"$containerBackupDir"), indent=2))
"@ | docker compose --env-file $EnvFilePath exec -T api python -
