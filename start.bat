@echo off
chcp 65001 >nul
echo SVN Auto Merge Tool Starting...
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found, please install Python 3.7+
    pause
    exit /b 1
)

REM Check virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check config file
if not exist "config.json" (
    echo Error: config.json not found
    echo Please configure branch paths and match rules first
    pause
    exit /b 1
)

REM Start program
echo Starting SVN Auto Merge Agent...
echo Starting Hook mode (real-time detection)...
python start_hook_system.py

pause