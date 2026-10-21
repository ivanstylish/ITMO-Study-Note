@echo off
setlocal
cd /d "%~dp0"
if defined LAB3_PYTHON goto run_selected
if exist "%~dp0.venv\Scripts\python.exe" (
    set "LAB3_PYTHON=%~dp0.venv\Scripts\python.exe"
    goto run_selected
)
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    set "LAB3_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    goto run_selected
)
py -3 -m lab3_color_sphere.main %*
if errorlevel 1 pause
exit /b
:run_selected
"%LAB3_PYTHON%" -m lab3_color_sphere.main %*
if errorlevel 1 pause
