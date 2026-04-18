param(
    [string]$BaseUrl = "https://localhost:8443"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot/helpers.ps1"

Write-Info "Running smoke checks against $BaseUrl"

$urls = @(
    "$BaseUrl/",
    "$BaseUrl/health/live",
    "$BaseUrl/health/ready",
    "$BaseUrl/health/startup"
)

foreach ($url in $urls) {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $url -SkipCertificateCheck -TimeoutSec 20
        if ($response.StatusCode -ne 200) {
            throw "Unexpected status code $($response.StatusCode) for $url"
        }
        Write-Info "PASS $url"
    } catch {
        Write-Fail "FAILED $url :: $($_.Exception.Message)"
        throw
    }
}
