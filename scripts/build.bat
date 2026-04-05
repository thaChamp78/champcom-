@echo off
REM ChampCom Build & Launch Script (Windows)

echo ===============================
echo   ChampCom Build System
echo ===============================

REM Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python 3 is required but not found.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create directories
mkdir configs 2>nul
mkdir assets 2>nul
mkdir modules 2>nul
mkdir logs 2>nul

echo [OK] All dependencies satisfied.
echo [OK] Launching ChampCom...
echo.

cd /d "%~dp0\.."
python main.py
pause
