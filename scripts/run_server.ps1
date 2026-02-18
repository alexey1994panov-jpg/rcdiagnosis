param(
    [Alias("Host")]
    [string]$BindHost = "0.0.0.0",
    [int]$Port = 8000,
    [switch]$Reload
)

$args = @("api.app:app", "--host", $BindHost, "--port", "$Port")
if ($Reload) {
    $args += "--reload"
}

python -m uvicorn @args
