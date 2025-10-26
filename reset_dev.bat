@echo off
REM Reset local development environment
echo 🔄 Resetting Local Development Environment
echo ========================================

echo ⚠️ This will delete your local database and reset everything!
set /p confirm="Are you sure? (y/N): "
if /i not "%confirm%"=="y" (
    echo ❌ Reset cancelled
    pause
    exit /b 0
)

echo 🗑️ Cleaning up...

REM Remove database
if exist "backend\app_data.db" (
    del "backend\app_data.db"
    echo ✅ Deleted local database
)

REM Remove Python cache
for /d /r %%i in (__pycache__) do (
    if exist "%%i" (
        rmdir /s /q "%%i" 2>nul
        echo ✅ Cleared Python cache
    )
)

REM Remove .pyc files
for /r %%i in (*.pyc) do (
    del "%%i" 2>nul
)

REM Optional: Remove virtual environment
set /p remove_venv="Remove virtual environment too? (y/N): "
if /i "%remove_venv%"=="y" (
    if exist "venv" (
        rmdir /s /q "venv"
        echo ✅ Removed virtual environment
    )
)

echo.
echo ✅ Reset complete!
echo 🚀 Run start_dev.bat to set up fresh environment
echo.

pause
