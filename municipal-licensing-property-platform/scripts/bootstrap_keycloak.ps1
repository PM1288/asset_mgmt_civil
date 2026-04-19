param(
    [string]$EnvFilePath = ".env"
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
. "$PSScriptRoot/helpers.ps1"

$envContent = Get-Content $EnvFilePath | Where-Object { $_ -match "=" } | ForEach-Object {
    $parts = $_ -split "=", 2
    [PSCustomObject]@{ Key = $parts[0]; Value = $parts[1] }
}
foreach ($pair in $envContent) {
    Set-Item -Path "Env:$($pair.Key)" -Value $pair.Value
}

Write-Info "Aligning Keycloak client redirect URIs and web origins to the configured hostname."
$realm = if ($env:KEYCLOAK_REALM) { $env:KEYCLOAK_REALM } else { "municipal" }
$httpPort = if ($env:HTTP_PORT) { $env:HTTP_PORT } else { "8080" }
$publicBaseUrl = if ($env:PUBLIC_BASE_URL) {
    $env:PUBLIC_BASE_URL.TrimEnd("/")
} else {
    "http://$($env:APP_HOSTNAME):$httpPort"
}
$redirectUri = "$publicBaseUrl/*"
$webOrigin = $publicBaseUrl

docker compose --env-file $EnvFilePath exec -T keycloak /opt/keycloak/bin/kcadm.sh config credentials `
  --server http://127.0.0.1:8080/auth `
  --realm master `
  --user $env:KEYCLOAK_ADMIN_USER `
  --password $env:KEYCLOAK_ADMIN_PASSWORD

$clientId = docker compose --env-file $EnvFilePath exec -T keycloak /opt/keycloak/bin/kcadm.sh get clients `
  -r $realm -q clientId=municipal-frontend --fields id --format csv --noquotes
$clientId = ($clientId | Select-Object -First 1).Trim()

docker compose --env-file $EnvFilePath exec -T keycloak /opt/keycloak/bin/kcadm.sh update "clients/$clientId" `
  -r $realm `
  -s ('redirectUris=["{0}"]' -f $redirectUri) `
  -s ('webOrigins=["{0}"]' -f $webOrigin)

Write-Info "Keycloak bootstrap complete. Optional LDAP federation remains a site-specific post-step."
