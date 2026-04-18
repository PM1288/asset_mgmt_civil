param(
    [string]$OutputEnvPath = ".env"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot/helpers.ps1"

function New-RandomPassword {
    param([int]$Length = 28)
    # Keep passwords URI-safe for DATABASE_URL and shell-safe for deployment scripts.
    $chars = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789_-"
    -join (1..$Length | ForEach-Object { $chars[(Get-Random -Minimum 0 -Maximum $chars.Length)] })
}

Write-Info "Generating local secrets and environment file."

Copy-Item ".env.example" $OutputEnvPath -Force

$bytes = New-Object byte[] 32
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$fernetKey = [Convert]::ToBase64String($bytes).Replace("+", "-").Replace("/", "_")
Set-Or-UpdateEnvValue -FilePath $OutputEnvPath -Key "APP_DB_PASSWORD" -Value (New-RandomPassword)
Set-Or-UpdateEnvValue -FilePath $OutputEnvPath -Key "KEYCLOAK_DB_PASSWORD" -Value (New-RandomPassword)
Set-Or-UpdateEnvValue -FilePath $OutputEnvPath -Key "KEYCLOAK_ADMIN_PASSWORD" -Value (New-RandomPassword)
Set-Or-UpdateEnvValue -FilePath $OutputEnvPath -Key "APP_ENCRYPTION_KEY" -Value $fernetKey

Write-Info "Generated $OutputEnvPath. Review and adjust hostnames and ports before deployment."
