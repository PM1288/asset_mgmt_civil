param(
    [string]$BackupDir,
    [string]$EnvFilePath = ".env"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot/helpers.ps1"

if (-not $BackupDir) {
    throw "BackupDir is required."
}

if (-not (Test-Path $EnvFilePath)) {
    throw "Env file not found at $EnvFilePath"
}

(Get-Content $EnvFilePath | Where-Object { $_ -match "=" }) | ForEach-Object {
    $parts = $_ -split "=", 2
    Set-Item -Path "Env:$($parts[0])" -Value $parts[1]
}

$manifestPath = Join-Path $BackupDir "manifest.json"
if (-not (Test-Path $manifestPath)) {
    throw "Manifest not found at $manifestPath"
}

$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
$dumpPathHost = Join-Path $BackupDir $manifest.database_dump
$docsPathHost = Join-Path $BackupDir $manifest.documents_archive
$dumpPathContainer = "/srv/backups/" + ([IO.Path]::GetFileName($BackupDir)) + "/" + $manifest.database_dump

Write-Warn "This operation stops API, worker and beat while restoring. Proceed carefully."
docker compose --env-file $EnvFilePath stop api worker beat

Write-Info "Restoring PostgreSQL database from $dumpPathContainer"
docker compose --env-file $EnvFilePath exec -T api pg_restore `
  --clean --if-exists --no-owner `
  --host db --port 5432 `
  --username $env:APP_DB_USER `
  --dbname $env:APP_DB_NAME `
  $dumpPathContainer

Write-Info "Restoring encrypted document archive."
if (Test-Path "runtime/documents") {
    Remove-Item -Recurse -Force "runtime/documents"
}
New-Item -ItemType Directory -Force -Path "runtime/documents" | Out-Null
tar -xzf $docsPathHost -C "runtime"

Write-Info "Starting services."
docker compose --env-file $EnvFilePath up -d api worker beat
