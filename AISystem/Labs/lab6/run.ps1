param(
    [ValidateSet('Train','Predict','Notebook','Check','Drawings','Report')][string]$Mode = 'Check',
    [string]$Image
)
$ErrorActionPreference = 'Stop'
$taskPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) { throw 'Run setup.ps1 first.' }
# Resolve the user's image before changing the working directory.
if ($Mode -eq 'Predict') {
    if (-not $Image) { throw 'Use -Image followed by the picture path.' }
    $Image = (Resolve-Path -LiteralPath $Image).Path
}
$taskOldPath, $taskOldUser, $taskOldMpl = $env:PYTHONPATH, $env:PYTHONNOUSERSITE, $env:MPLCONFIGDIR
$taskOldThreads, $taskOldOmp = $env:OPENBLAS_NUM_THREADS, $env:OMP_NUM_THREADS
$taskOldTemp, $taskOldTmp = $env:TEMP, $env:TMP
$taskOldIPython = $env:IPYTHONDIR
$taskOldConfig, $taskOldData, $taskOldRuntime = $env:JUPYTER_CONFIG_DIR, $env:JUPYTER_DATA_DIR, $env:JUPYTER_RUNTIME_DIR
try {
    $env:PYTHONPATH = $null
    $env:PYTHONNOUSERSITE = '1'
    $env:MPLCONFIGDIR = Join-Path $PSScriptRoot '.cache\matplotlib'
    $env:OPENBLAS_NUM_THREADS = '2'
    $env:OMP_NUM_THREADS = '2'
    $env:TEMP = Join-Path $PSScriptRoot '.cache\tmp'
    $env:TMP = $env:TEMP
    $env:IPYTHONDIR = Join-Path $PSScriptRoot '.cache\ipython'
    $env:JUPYTER_CONFIG_DIR = Join-Path $PSScriptRoot '.cache\jupyter-config'
    $env:JUPYTER_DATA_DIR = Join-Path $PSScriptRoot '.cache\jupyter-data'
    $env:JUPYTER_RUNTIME_DIR = Join-Path $PSScriptRoot '.cache\jupyter-runtime'
    New-Item -ItemType Directory -Force $env:TEMP,$env:IPYTHONDIR,$env:JUPYTER_CONFIG_DIR,$env:JUPYTER_DATA_DIR,$env:JUPYTER_RUNTIME_DIR | Out-Null
    Push-Location -LiteralPath $PSScriptRoot
    try {
        switch ($Mode) {
            Train { & $taskPython -m mnist_lab train }
            Predict { & $taskPython -m mnist_lab predict $Image }
            Drawings { & $taskPython -m mnist_lab drawings }
            Report { & $taskPython build_report.py }
            Notebook { & $taskPython -m jupyterlab --notebook-dir $PSScriptRoot }
            Check {
                & $taskPython -m pip check
                if ($LASTEXITCODE -ne 0) { throw 'Dependency check failed.' }
                & $taskPython -m unittest -v
            }
        }
        if ($LASTEXITCODE -ne 0) { throw "Mode $Mode failed." }
    } finally { Pop-Location }
} finally {
    $env:PYTHONPATH, $env:PYTHONNOUSERSITE, $env:MPLCONFIGDIR = $taskOldPath, $taskOldUser, $taskOldMpl
    $env:OPENBLAS_NUM_THREADS, $env:OMP_NUM_THREADS = $taskOldThreads, $taskOldOmp
    $env:TEMP, $env:TMP = $taskOldTemp, $taskOldTmp
    $env:IPYTHONDIR = $taskOldIPython
    $env:JUPYTER_CONFIG_DIR, $env:JUPYTER_DATA_DIR, $env:JUPYTER_RUNTIME_DIR = $taskOldConfig, $taskOldData, $taskOldRuntime
}
