@echo off
REM Quick test script for local development
echo 🧪 Testing Auction Monitor - Local Development
echo =============================================

echo 📡 Testing backend health...
curl -s http://localhost:5000/ > nul
if errorlevel 1 (
    echo ❌ Backend is not running! Start it with start_dev.bat first
    pause
    exit /b 1
)

echo ✅ Backend is running!
echo.

echo 📊 Getting system stats...
curl -s "http://localhost:5000/api/stats"
echo.
echo.

echo 🤖 Testing cron endpoint...
curl -s "http://localhost:5000/cron/local-development-secret-key"
echo.
echo.

echo 📋 Testing status endpoint...
curl -s "http://localhost:5000/cron-status/local-development-secret-key"
echo.
echo.

echo ✅ All tests completed!
echo.
echo 💡 Tips:
echo - Add listeners through the web interface (frontend/index.html)
echo - Test email with: curl -X POST "http://localhost:5000/api/test-email" -H "Content-Type: application/json" -d "{\"email\":\"your@email.com\"}"
echo - Check logs in the terminal where you started the backend
echo.

pause
