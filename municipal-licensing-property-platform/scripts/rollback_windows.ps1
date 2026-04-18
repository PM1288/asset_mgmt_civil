param(
    [string]$EnvFilePath = ".env"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot/helpers.ps1"

function Get-EnvValue {
    param(
        [string]$FilePath,
        [string]$Key,
        [string]$DefaultValue = ""
    )
    if (-not (Test-Path $FilePath)) {
        return $DefaultValue
    }
    $match = Get-Content $FilePath | Where-Object { $_ -match "^$Key=" } | Select-Object -First 1
    if (-not $match) {
        return $DefaultValue
    }
    return ($match -split "=", 2)[1]
}

if (-not (Test-Path "runtime/app/release_state.json")) {
    throw "No release_state.json found."
}

$state = Get-Content "runtime/app/release_state.json" -Raw | ConvertFrom-Json
if (-not $state.previous) {
    throw "No previous release tag is recorded."
}

Set-Or-UpdateEnvValue -FilePath $EnvFilePath -Key "RELEASE_TAG" -Value $state.previous

Write-Info "Rolling back to release tag $($state.previous)"
docker compose --env-file $EnvFilePath up -d api worker beat frontend proxy

$appHost = Get-EnvValue -FilePath $EnvFilePath -Key "APP_HOSTNAME" -DefaultValue "localhost"
& "$PSScriptRoot/healthcheck_smoke_test.ps1" -BaseUrl "https://$appHost:8443"

$newState = @{
    current = $state.previous
    previous = $state.current
    deployedAt = (Get-Date).ToString("o")
} | ConvertTo-Json
Set-Content -Path "runtime/app/release_state.json" -Value $newState -Encoding UTF8

Write-Info "Rollback completed."
