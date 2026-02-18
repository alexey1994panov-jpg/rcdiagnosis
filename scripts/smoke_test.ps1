param(
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 8010,
    [string]$PythonExe = ".\.venv\Scripts\python.exe",
    [switch]$RunPytest
)

$ErrorActionPreference = "Stop"

function Resolve-Python {
    param([string]$Preferred)
    if ($Preferred -and (Test-Path $Preferred)) {
        return (Resolve-Path $Preferred).Path
    }
    return "python"
}

$py = Resolve-Python -Preferred $PythonExe
Write-Host "[smoke] Python: $py"

Write-Host "[smoke] Import check api.engine_app ..."
& $py -c "import api.engine_app as e; print(bool(e.app))"
if ($LASTEXITCODE -ne 0) {
    throw "[smoke] import check failed"
}

if ($RunPytest) {
    Write-Host "[smoke] Running pytest ..."
    & $py -m pytest -q
    if ($LASTEXITCODE -ne 0) {
        throw "[smoke] pytest failed"
    }
}

$stdoutLog = Join-Path $env:TEMP "rcdiag_smoke_uvicorn_out.log"
$stderrLog = Join-Path $env:TEMP "rcdiag_smoke_uvicorn_err.log"
if (Test-Path $stdoutLog) { Remove-Item $stdoutLog -Force }
if (Test-Path $stderrLog) { Remove-Item $stderrLog -Force }

Write-Host "[smoke] Starting server on http://$BindHost`:$Port ..."
$proc = Start-Process -FilePath $py `
    -ArgumentList @("-m", "uvicorn", "api.app:app", "--host", $BindHost, "--port", "$Port") `
    -PassThru `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog

try {
    $ok = $false
    for ($i = 0; $i -lt 25; $i++) {
        Start-Sleep -Milliseconds 400
        try {
            $resp = Invoke-WebRequest -Uri "http://$BindHost`:$Port/health" -UseBasicParsing -TimeoutSec 2
            if ($resp.StatusCode -eq 200) {
                $ok = $true
                Write-Host "[smoke] /health OK: $($resp.Content)"
                break
            }
        } catch {
            # retry
        }
    }

    if (-not $ok) {
        Write-Host "[smoke] Server logs (stdout):"
        if (Test-Path $stdoutLog) { Get-Content $stdoutLog -ErrorAction SilentlyContinue }
        Write-Host "[smoke] Server logs (stderr):"
        if (Test-Path $stderrLog) { Get-Content $stderrLog -ErrorAction SilentlyContinue }
        throw "[smoke] health check failed"
    }

    Write-Host "[smoke] SUCCESS"
}
finally {
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force
    }
}

