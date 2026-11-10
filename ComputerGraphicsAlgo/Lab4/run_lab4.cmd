@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m lab4_spectrum %*
) else (
  python -m lab4_spectrum %*
)
if errorlevel 1 pause
