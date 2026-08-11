# Powershell Launcher & Interactive Web Test Runner Opener
$htmlPath = Join-Path $PSScriptRoot "test_runner.html"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Risk-Based HCP Identity Resolution Test Runner" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening interactive test runner in your default web browser..." -ForegroundColor Yellow
Write-Host "File: $htmlPath" -ForegroundColor Gray

Start-Process $htmlPath

Write-Host "Test runner launched successfully!" -ForegroundColor Green
