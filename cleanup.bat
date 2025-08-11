@echo off
echo 🧹 Cleaning up Auction Listener project...
echo.

cd /d "%~dp0"

echo Removing debug files...
if exist "backend\check_*.py" del /Q "backend\check_*.py"
if exist "backend\clear_*.py" del /Q "backend\clear_*.py"
if exist "backend\debug_*.py" del /Q "backend\debug_*.py"
if exist "backend\test_*.py" del /Q "backend\test_*.py"
if exist "backend\inspect_*.py" del /Q "backend\inspect_*.py"

echo Removing duplicate scrapers...
if exist "backend\improved_scraper*.py" del /Q "backend\improved_scraper*.py"
if exist "backend\selenium_scraper.py" del /Q "backend\selenium_scraper.py"
if exist "backend\scraper.py" del /Q "backend\scraper.py"
if exist "backend\js_scraper.py" del /Q "backend\js_scraper.py"
if exist "backend\manual_check_selenium.py" del /Q "backend\manual_check_selenium.py"

echo Removing development docs...
if exist "CLEANUP_SUMMARY.md" del /Q "CLEANUP_SUMMARY.md"
if exist "DYNAMIC_TERMS_CONFIRMED.md" del /Q "DYNAMIC_TERMS_CONFIRMED.md"
if exist "SCRAPER_UPDATES.md" del /Q "SCRAPER_UPDATES.md"
if exist "SYSTEM_STATUS.md" del /Q "SYSTEM_STATUS.md"

echo Removing root test files...
if exist "check_status.py" del /Q "check_status.py"
if exist "start.py" del /Q "start.py"
if exist "test_*.py" del /Q "test_*.py"

echo Removing cache...
if exist "backend\__pycache__" rmdir /S /Q "backend\__pycache__"

echo.
echo ✅ Cleanup complete! Production files only.
echo.
echo Production structure:
echo   backend/ (12 files)
echo   frontend/ (3 files)
echo   README.md
echo   start.bat
echo.
pause
