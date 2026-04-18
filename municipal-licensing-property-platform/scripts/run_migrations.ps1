param(
    [string]$ComposeFile = "docker-compose.yml",
    [string]$EnvFilePath = ".env"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot/helpers.ps1"

Write-Info "Running alembic migrations through Docker Compose."
docker compose --env-file $EnvFilePath -f $ComposeFile run --rm migrations
