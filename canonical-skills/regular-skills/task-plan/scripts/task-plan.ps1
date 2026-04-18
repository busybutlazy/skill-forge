# task-plan.ps1 — thin wrapper that delegates to task-plan-core.py
# Run from the project root directory.

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$python = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $python) {
    Write-Error "python3 is required but not installed."
    exit 1
}

& $python.Source "$scriptDir\task-plan-core.py" @args
