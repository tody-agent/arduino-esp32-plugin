param(
    [int]$Port = 8321
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$pythonScript = Join-Path $scriptDir "log_dashboard.py"

if (-not (Test-Path $pythonScript)) {
    Write-Error "Could not find log_dashboard.py at $pythonScript"
    exit 1
}

Write-Host "Khởi chạy ESP32 Visual Log Debugger trên http://localhost:$Port..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "`"$pythonScript`"" -NoNewWindow
