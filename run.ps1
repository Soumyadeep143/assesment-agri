# Starts the backend (FastAPI/uvicorn) and frontend (Vite) together.
# Usage (PowerShell): .\run.ps1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$Py = Join-Path $Root "venv\Scripts\python.exe"
if (-not (Test-Path $Py)) {
    Write-Output "venv not found at $Root\venv - create it first:"
    Write-Output "  python -m venv venv; .\venv\Scripts\python.exe -m pip install -r requirements.txt"
    exit 1
}

$FrontendDir = Join-Path $Root "frontend"
if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    Write-Output "Installing frontend dependencies..."
    Push-Location $FrontendDir
    npm install
    Pop-Location
}

$EnvFile = Join-Path $FrontendDir ".env"
if (-not (Test-Path $EnvFile)) {
    Copy-Item (Join-Path $FrontendDir ".env.example") $EnvFile
}

$LogsDir = Join-Path $Root ".logs"
New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null

$npmCmd = Join-Path (Split-Path (Get-Command npm).Source) "npm.cmd"

Write-Output "Starting backend (FastAPI) on :8000 ..."
$backend = Start-Process -FilePath $Py `
    -ArgumentList "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000" `
    -WorkingDirectory $Root `
    -RedirectStandardOutput (Join-Path $LogsDir "backend.log") `
    -RedirectStandardError (Join-Path $LogsDir "backend.err.log") `
    -PassThru -NoNewWindow

Write-Output "Starting frontend (Vite) on :5173 ..."
$frontend = Start-Process -FilePath $npmCmd -ArgumentList "run", "dev" `
    -WorkingDirectory $FrontendDir `
    -RedirectStandardOutput (Join-Path $LogsDir "frontend.log") `
    -RedirectStandardError (Join-Path $LogsDir "frontend.err.log") `
    -PassThru -NoNewWindow

Write-Output ""
Write-Output "Backend:  http://localhost:8000  (logs: .logs\backend.log)"
Write-Output "Frontend: http://localhost:5173  (logs: .logs\frontend.log)"
Write-Output "Press Ctrl+C to stop both."
Write-Output ""

try {
    Wait-Process -Id $backend.Id, $frontend.Id
}
finally {
    Write-Output ""
    Write-Output "Stopping backend (pid $($backend.Id)) and frontend (pid $($frontend.Id))..."
    Stop-Process -Id $backend.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $frontend.Id -ErrorAction SilentlyContinue
}
