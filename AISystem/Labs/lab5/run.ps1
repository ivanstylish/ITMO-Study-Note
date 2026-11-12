$ErrorActionPreference = 'Stop'
$taskPython = $env:AISYSTEM_PYTHON
if (-not $taskPython) {
    $taskPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
}
if (-not (Test-Path -LiteralPath $taskPython)) {
    throw 'Create .venv with Python 3.10+ and install requirements.txt first. See README.md.'
}
& $taskPython -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10+ is required'"
if ($LASTEXITCODE -ne 0) { throw 'Unsupported Python version.' }
$taskOldPath, $taskOldMpl, $taskOldUserSite = $env:PYTHONPATH, $env:MPLCONFIGDIR, $env:PYTHONNOUSERSITE
try {
    $env:PYTHONPATH = $null
    $env:PYTHONNOUSERSITE = '1'
    $env:MPLCONFIGDIR = Join-Path $PSScriptRoot '_qa\matplotlib'
    Push-Location -LiteralPath $PSScriptRoot
    try {
        & $taskPython experiment.py
        if ($LASTEXITCODE -ne 0) { throw 'Experiment failed. Check requirements.txt.' }
        & $taskPython -m unittest -v test_decision_tree.py
        if ($LASTEXITCODE -ne 0) { throw 'Verification failed.' }
    } finally { Pop-Location }
} finally {
    $env:PYTHONPATH, $env:MPLCONFIGDIR, $env:PYTHONNOUSERSITE = $taskOldPath, $taskOldMpl, $taskOldUserSite
}
