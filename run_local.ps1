# PowerShell helper to run Event Eye locally (Windows)
# Usage: Open PowerShell in project root and run: .\run_local.ps1

Write-Host "Activating venv (if exists)..."
if (Test-Path .\venv\Scripts\Activate.ps1) {
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "No virtual environment found. Create one with: python -m venv venv"
}

# Example: set your email and app password in this session
if (-not $env:SENDER_EMAIL) {
    Write-Host "You can set SENDER_EMAIL now (press Enter to skip)"
    $e = Read-Host "SENDER_EMAIL"
    if ($e -ne "") { $env:SENDER_EMAIL = $e }
}
if (-not $env:SENDER_PASSWORD) {
    Write-Host "You can set SENDER_PASSWORD now (press Enter to skip)"
    $p = Read-Host "SENDER_PASSWORD"
    if ($p -ne "") { $env:SENDER_PASSWORD = $p }
}

Write-Host "Starting app..."
python .\app.py
