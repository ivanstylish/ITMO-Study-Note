param([switch]$NoPlots, [switch]$SkipChecks)
$ErrorActionPreference = 'Stop'
$taskCandidates = @()
if ($env:AISYSTEM_PYTHON) { $taskCandidates += $env:AISYSTEM_PYTHON }
$taskCandidates += Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$taskNormalPython = Get-Command python.exe -ErrorAction SilentlyContinue
if ($taskNormalPython -and $taskNormalPython.Source -notmatch 'WindowsApps') {
    $taskCandidates += $taskNormalPython.Source
}
$taskCandidates += Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$taskPython = $null
foreach ($taskCandidate in $taskCandidates) {
    if (-not (Test-Path -LiteralPath $taskCandidate -PathType Leaf)) { continue }
    try {
        & $taskCandidate -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' 2>$null
        if ($LASTEXITCODE -eq 0) { $taskPython = $taskCandidate; break }
    } catch { continue }
}
if (-not $taskPython) { throw 'Install Python 3.10+ or set AISYSTEM_PYTHON to the interpreter path.' }
$taskOriginalPythonPath = $env:PYTHONPATH
$taskOriginalMplPath = $env:MPLCONFIGDIR
$taskOriginalEncoding = $env:PYTHONIOENCODING
try {
    $taskLibraries = Join-Path $PSScriptRoot '_qa\dependencies'
    if (Test-Path -LiteralPath $taskLibraries) {
        $env:PYTHONPATH = $taskLibraries + [System.IO.Path]::PathSeparator + $env:PYTHONPATH
    }
    $env:MPLCONFIGDIR = Join-Path $PSScriptRoot '_qa\matplotlib'
    $env:PYTHONIOENCODING = 'utf-8'
    $taskArgs = @((Join-Path $PSScriptRoot 'regularization.py'))
    if ($NoPlots) { $taskArgs += '--no-plots' }
    & $taskPython @taskArgs
    if ($LASTEXITCODE -ne 0) { throw 'Experiment failed; install the packages in requirements.txt if dependencies are missing.' }
    if (-not $SkipChecks) {
        Push-Location -LiteralPath $PSScriptRoot
        try {
            & $taskPython -m unittest -v test_regularization.py
            if ($LASTEXITCODE -ne 0) { throw 'Numerical verification failed.' }
        } finally { Pop-Location }
    }
} finally {
    $env:PYTHONPATH = $taskOriginalPythonPath
    $env:MPLCONFIGDIR = $taskOriginalMplPath
    $env:PYTHONIOENCODING = $taskOriginalEncoding
}
