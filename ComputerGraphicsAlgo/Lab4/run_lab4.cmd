@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" lab4.py %*
) else (
  python lab4.py %*
)
if errorlevel 1 pause
