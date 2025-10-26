@echo off
REM Local Development Startup Script for Windows
echo 🛠️ Auction Monitor - Local Development Setup
echo ==========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update requirements
echo 📥 Installing/updating dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚙️ Creating development environment file...
    copy .env.development .env >nul
    echo ✅ Created .env file from template
    echo ❗ IMPORTANT: Edit .env file with your Gmail credentials
    echo.
)

REM Start the application
echo 🚀 Starting Auction Monitor in development mode...
echo.
echo 📡 Backend will be available at: http://localhost:5000
echo 🌐 Open frontend/index.html in your browser
echo.
echo Press Ctrl+C to stop the server
echo ==========================================
python app.py

pause
