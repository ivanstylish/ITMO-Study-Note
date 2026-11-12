param([string]$Python = 'py')
$ErrorActionPreference = 'Stop'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONPATH = $null
$env:TEMP = Join-Path $PSScriptRoot '.cache\tmp'
$env:TMP = $env:TEMP
$env:IPYTHONDIR = Join-Path $PSScriptRoot '.cache\ipython'
New-Item -ItemType Directory -Force $env:TEMP,$env:IPYTHONDIR | Out-Null
$taskVenv = Join-Path $PSScriptRoot '.venv'
$taskPython = Join-Path $taskVenv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) {
    if ($Python -eq 'py') { & $Python -3.12 -m venv $taskVenv }
    else { & $Python -m venv $taskVenv }
    if ($LASTEXITCODE -ne 0) { throw 'Could not create Python 3.12 environment.' }
}
& $taskPython -c "import sys; assert sys.version_info[:2] == (3, 12), 'Use Python 3.12'"
if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 is required.' }
& $taskPython -m ensurepip --upgrade
if ($LASTEXITCODE -ne 0) { throw 'pip initialization failed.' }
$taskRequirements = Join-Path $PSScriptRoot 'requirements-lock.txt'
if (-not (Test-Path -LiteralPath $taskRequirements)) { $taskRequirements = Join-Path $PSScriptRoot 'requirements.txt' }
& $taskPython -m pip install -r $taskRequirements
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& $taskPython -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency check failed.' }
& $taskPython -m ipykernel install --prefix $taskVenv --name python3 --display-name 'Python 3 (Lab 6 .venv)'
if ($LASTEXITCODE -ne 0) { throw 'Notebook kernel installation failed.' }
Write-Host 'Environment ready. Use run.ps1 -Mode Check.'
