param(
    [string]$RepoUrl = "",
    [string]$DeployPath = (Get-Location).Path,
    [string]$EnvFilePath = "",
    [string]$DomainOrHostname = "localhost",
    [string]$AdminEmail = "admin@example.local"
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
. "$PSScriptRoot/helpers.ps1"

Assert-Command git
Assert-Command docker

Write-Info "Preparing deployment at $DeployPath"
Ensure-Directory $DeployPath

if ($RepoUrl) {
    if (Test-Path (Join-Path $DeployPath ".git")) {
        Write-Info "Repository already present. Pulling latest changes."
        git -C $DeployPath fetch --all
        git -C $DeployPath pull --ff-only
    } else {
        Write-Info "Cloning repository from $RepoUrl"
        git clone $RepoUrl $DeployPath
    }
}

Set-Location $DeployPath

if (-not $EnvFilePath) {
    $EnvFilePath = Join-Path $DeployPath ".env"
}

if (-not (Test-Path $EnvFilePath)) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" $EnvFilePath -Force
    } else {
        throw ".env.example was not found and no EnvFilePath was supplied."
    }
}

Set-Or-UpdateEnvValue -FilePath $EnvFilePath -Key "APP_HOSTNAME" -Value $DomainOrHostname

$previousTag = ""
if (Test-Path "runtime/app/release_state.json") {
    try {
        $state = Get-Content "runtime/app/release_state.json" -Raw | ConvertFrom-Json
        $previousTag = $state.current
    } catch {
        $previousTag = ""
    }
}

$releaseTag = Get-GitShortSha
Set-Or-UpdateEnvValue -FilePath $EnvFilePath -Key "RELEASE_TAG" -Value $releaseTag

Ensure-Directory "runtime/backups"
Ensure-Directory "runtime/documents"
Ensure-Directory "runtime/logs/api"
Ensure-Directory "runtime/logs/worker"
Ensure-Directory "runtime/logs/beat"
Ensure-Directory "runtime/app"

Write-Info "Building containers with release tag $releaseTag"
docker compose --env-file $EnvFilePath build api frontend

Write-Info "Starting foundational services"
docker compose --env-file $EnvFilePath up -d db keycloak-db redis
Start-Sleep -Seconds 10
docker compose --env-file $EnvFilePath up -d keycloak

Write-Info "Running schema migrations"
docker compose --env-file $EnvFilePath run --rm migrations

Write-Info "Starting application services"
docker compose --env-file $EnvFilePath up -d api worker beat frontend proxy

Write-Info "Configuring Keycloak client settings"
& "$PSScriptRoot/bootstrap_keycloak.ps1" -EnvFilePath $EnvFilePath

Write-Info "Running smoke checks"
$httpsPort = "8443"
$httpsPortLine = Get-Content $EnvFilePath | Where-Object { $_ -match "^HTTPS_PORT=" } | Select-Object -Last 1
if ($httpsPortLine) {
    $httpsPort = ($httpsPortLine -split "=", 2)[1].Trim()
}
$smokeBaseUrl = "https://$($DomainOrHostname):$httpsPort"
& "$PSScriptRoot/healthcheck_smoke_test.ps1" -BaseUrl $smokeBaseUrl

$state = @{
    current = $releaseTag
    previous = $previousTag
    deployedAt = (Get-Date).ToString("o")
} | ConvertTo-Json
Set-Content -Path "runtime/app/release_state.json" -Value $state -Encoding UTF8

Write-Info "Deployment complete."
