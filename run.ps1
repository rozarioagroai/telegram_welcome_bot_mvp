param(
    [switch]$NoInstall  # можно вызвать: .\run.ps1 -NoInstall (пропустит pip install)
)
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$venvPy = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPy)) {
    & py -3.11 -m venv (Join-Path $root ".venv")
}
if (-not $NoInstall) {
    & $venvPy -m pip install -r (Join-Path $root "requirements.txt")
}
& $venvPy -m src.bot_app