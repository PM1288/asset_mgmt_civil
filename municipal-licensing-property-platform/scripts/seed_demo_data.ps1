param(
    [string]$ComposeFile = "docker-compose.yml",
    [string]$EnvFilePath = ".env",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot/helpers.ps1"

Write-Info "Seeding demo data through the running API container."

$arguments = @("--env-file", $EnvFilePath, "-f", $ComposeFile, "exec", "-T", "api", "python", "-m", "app.tools.seed_demo_data")
if ($Force) {
    $arguments += "--force"
}

docker compose @arguments
