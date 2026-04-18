function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Fail {
    param([string]$Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Assert-Command {
    param([string]$CommandName)
    if (-not (Get-Command $CommandName -ErrorAction SilentlyContinue)) {
        throw "Required command '$CommandName' was not found in PATH."
    }
}

function Wait-ForHttp200 {
    param(
        [string]$Url,
        [int]$Attempts = 60,
        [int]$SleepSeconds = 5
    )
    for ($i = 0; $i -lt $Attempts; $i++) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                return $true
            }
        } catch {
            Start-Sleep -Seconds $SleepSeconds
        }
    }
    return $false
}

function Set-Or-UpdateEnvValue {
    param(
        [string]$FilePath,
        [string]$Key,
        [string]$Value
    )

    if (-not (Test-Path $FilePath)) {
        New-Item -ItemType File -Path $FilePath -Force | Out-Null
    }

    $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
    if ($content -match "(?m)^$Key=") {
        $updated = [regex]::Replace($content, "(?m)^$Key=.*$", "$Key=$Value")
        Set-Content -Path $FilePath -Value $updated -Encoding UTF8
    } else {
        Add-Content -Path $FilePath -Value "$Key=$Value"
    }
}

function Ensure-Directory {
    param([string]$PathToCreate)
    if (-not (Test-Path $PathToCreate)) {
        New-Item -ItemType Directory -Path $PathToCreate -Force | Out-Null
    }
}

function Get-GitShortSha {
    try {
        return (git rev-parse --short HEAD).Trim()
    } catch {
        return (Get-Date -Format "yyyyMMddHHmmss")
    }
}
