@echo off
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python。请先安装 Python 3.10+：https://www.python.org/downloads/
    echo 安装时勾选 "Add Python to PATH"。
    pause
    exit /b 1
)

set "VENV_PY=.venv\Scripts\python.exe"
set "VENV_ACT=.venv\Scripts\activate.bat"

if not exist "%VENV_PY%" (
    if exist "..\.venv\Scripts\python.exe" (
        set "VENV_PY=..\.venv\Scripts\python.exe"
        set "VENV_ACT=..\.venv\Scripts\activate.bat"
    ) else (
        echo 首次运行，正在创建虚拟环境并安装依赖...
        python -m venv .venv
        call .venv\Scripts\activate.bat
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        goto :run
    )
)

call "%VENV_ACT%"

:run
echo.
echo 启动 Phone Touchpad — WiFi 版...
python server\main.py
pause
