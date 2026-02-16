param(
    [string]$Host = "0.0.0.0",
    [int]$Port = 8000,
    [switch]$Reload
)

$args = @("api.app:app", "--host", $Host, "--port", "$Port")
if ($Reload) {
    $args += "--reload"
}

python -m uvicorn @args
