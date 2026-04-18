param(
    [string]$OutputZip = "municipal-licensing-property-platform.zip"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot/helpers.ps1"

Write-Info "Packaging repository into $OutputZip"

$items = Get-ChildItem -Force -Exclude ".git", "node_modules", "dist"
if (Test-Path $OutputZip) {
    Remove-Item $OutputZip -Force
}
Compress-Archive -Path $items.FullName -DestinationPath $OutputZip -Force
Write-Info "Package created."
