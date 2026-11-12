$ErrorActionPreference = 'Stop'
$taskPython = $env:AISYSTEM_PYTHON
if (-not $taskPython) {
    $taskPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
}
if (-not (Test-Path -LiteralPath $taskPython -PathType Leaf)) {
    throw 'Create .venv with: python -m venv .venv; then .venv\Scripts\python -m pip install -r requirements.txt'
}
$taskOldMpl, $taskOldEncoding = $env:MPLCONFIGDIR, $env:PYTHONIOENCODING
try {
    $env:MPLCONFIGDIR = Join-Path $PSScriptRoot '_qa\matplotlib'
    $env:PYTHONIOENCODING = 'utf-8'
    & $taskPython (Join-Path $PSScriptRoot 'experiment.py')
    if ($LASTEXITCODE -ne 0) { throw 'Experiment failed. Check requirements.txt.' }
    Push-Location -LiteralPath $PSScriptRoot
    try {
        & $taskPython -m unittest -v test_knn.py
        if ($LASTEXITCODE -ne 0) { throw 'Verification failed.' }
    } finally { Pop-Location }
} finally {
    $env:MPLCONFIGDIR, $env:PYTHONIOENCODING = $taskOldMpl, $taskOldEncoding
}
