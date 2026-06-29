@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ and add to PATH.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

rem Prefer root venv, then wifi venv, else create wifi venv
set "VENV_PY="
if exist "..\.venv\Scripts\python.exe" set "VENV_PY=..\.venv\Scripts\python.exe"
if not defined VENV_PY if exist ".venv\Scripts\python.exe" set "VENV_PY=.venv\Scripts\python.exe"

if not defined VENV_PY (
    echo First run: creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    set "VENV_PY=.venv\Scripts\python.exe"
    echo Installing dependencies...
    "%VENV_PY%" -m pip install --upgrade pip
    "%VENV_PY%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo.
echo Starting Phone Touchpad WiFi...
"%VENV_PY%" server\main.py
pause
