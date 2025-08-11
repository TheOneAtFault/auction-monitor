@echo off
echo Aucor Auction Listener - Windows Startup Script
echo =============================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://python.org
    pause
    exit /b 1
)

:: Run the startup script
python run_app.py

pause
