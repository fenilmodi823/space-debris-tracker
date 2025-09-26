# Run from repo root in VS Code terminal (PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "Creating virtual environment (if missing)..." -ForegroundColor Cyan
if (!(Test-Path -Path ".venv")) {
  py -m venv .venv
}
Write-Host "Activating venv..." -ForegroundColor Cyan
. .\.venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..." -ForegroundColor Cyan
python -m pip install -U pip
pip install -r requirements.txt

Write-Host "Running health check..." -ForegroundColor Cyan
python backend/scripts/health_check.py

