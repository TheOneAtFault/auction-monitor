# 🛠️ Local Development Guide - Auction Monitor

This guide will help you set up, run, and debug your auction monitor application locally on your Windows machine.

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ **Python 3.7+** installed
- ✅ **Git** installed (for version control)
- ✅ **Code editor** (VS Code recommended)
- ✅ **Chrome browser** (for Selenium scraping)
- ✅ **Gmail account** with App Password

## 🚀 Quick Start (5 Minutes)

### Step 1: Set Up Environment

1. **Open Command Prompt or PowerShell** in your project directory:
   ```powershell
   cd "d:\_Vault\Source\DefaultDirectory\auction-monitor"
   ```

2. **Create Python virtual environment**:
   ```powershell
   python -m venv venv
   ```

3. **Activate virtual environment**:
   ```powershell
   # Windows Command Prompt
   venv\Scripts\activate
   
   # Windows PowerShell
   venv\Scripts\Activate.ps1
   
   # If you get execution policy error in PowerShell:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Install dependencies**:
   ```powershell
   cd backend
   pip install -r requirements.txt
   ```

### Step 2: Configure Environment

1. **Copy development environment file**:
   ```powershell
   copy .env.development .env
   ```

2. **Edit .env file** with your Gmail credentials:
   ```
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-16-character-app-password
   ```

3. **Generate Gmail App Password** (if you haven't already):
   - Go to: https://security.google.com/settings/security/apppasswords
   - Select "Mail" → "Other" → Type "Auction Monitor Dev"
   - Copy the 16-character password to your .env file

### Step 3: Run the Application

1. **Start the backend**:
   ```powershell
   cd backend
   python app.py
   ```
   
   You should see:
   ```
   🔧 Starting in DEVELOPMENT mode
   📡 Server will be available at: http://127.0.0.1:5000
   🌐 Frontend should use: http://localhost:5000/api
   * Running on http://127.0.0.1:5000
   ```

2. **Open the frontend**:
   - Navigate to `frontend` folder
   - Open `index.html` in your browser
   - Or use VS Code Live Server extension

## 🔧 Development Features

### Debug Mode Enabled
- **Detailed error messages** in browser
- **Auto-reload** when code changes (Flask debug mode)
- **Verbose logging** to console
- **Stack traces** for easier debugging

### Local Database
- **SQLite database** created in `backend/app_data.db`
- **Persistent between runs** (data is saved)
- **Easy to reset** (just delete the file)

### Testing Endpoints
Your local server provides these endpoints:

```
📊 Main API:
http://localhost:5000/                     - Health check
http://localhost:5000/api/stats            - System statistics
http://localhost:5000/api/listeners        - Manage listeners

🤖 Cron Endpoints (for testing):
http://localhost:5000/cron/local-development-secret-key        - Trigger auction check
http://localhost:5000/cron-status/local-development-secret-key - Check status

📧 Email Testing:
POST http://localhost:5000/api/test-email  - Send test email
```

## 🧪 Testing Your Setup

### 1. Test Basic Functionality

**Health Check**:
```powershell
curl http://localhost:5000/
```

**Expected Response**:
```json
{
    "status": "running",
    "message": "Aucor Auction Listener API is running"
}
```

### 2. Test Email Sending

**Send Test Email**:
```powershell
curl -X POST "http://localhost:5000/api/test-email" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"your-email@gmail.com\"}"
```

### 3. Test Auction Scraping

**Trigger Manual Check**:
```powershell
curl "http://localhost:5000/cron/local-development-secret-key"
```

**Check Response** - should show scraping results and any notifications sent.

### 4. Test Frontend Integration

1. **Open** `frontend/index.html` in your browser
2. **Add a test listener** with your email
3. **Send test email** to verify email works
4. **Check browser console** for any JavaScript errors

## 🐛 Debugging Tips

### Common Issues & Solutions

**1. "Module not found" errors**:
```powershell
# Make sure virtual environment is activated
venv\Scripts\activate

# Reinstall requirements
pip install -r requirements.txt
```

**2. "Permission denied" or execution policy errors**:
```powershell
# Fix PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**3. "Chrome/ChromeDriver not found"**:
```powershell
# The app will automatically fall back to basic scraper
# Check console logs for "Using fallback scraper" message
```

**4. Email not sending**:
- Verify Gmail App Password is correct (16 characters, no spaces)
- Check if 2-Factor Authentication is enabled
- Try with different email provider

**5. CORS errors in frontend**:
- Make sure backend is running on http://localhost:5000
- Check browser console for detailed error messages

### Debugging with VS Code

1. **Install Python extension** for VS Code
2. **Set up launch configuration** (`.vscode/launch.json`):
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Flask",
               "type": "python",
               "request": "launch",
               "program": "${workspaceFolder}/backend/app.py",
               "env": {
                   "FLASK_ENV": "development"
               },
               "console": "integratedTerminal",
               "cwd": "${workspaceFolder}/backend"
           }
       ]
   }
   ```

3. **Set breakpoints** in your Python code
4. **Press F5** to start debugging

### View Logs and Database

**Check Application Logs**:
- Logs appear in the terminal where you run `python app.py`
- Look for 🔧, 📧, 📦, ✅, ❌ emoji indicators

**Inspect Database**:
```powershell
# Install SQLite browser (optional)
# Or use VS Code SQLite extension

# View database file
sqlite3 backend/app_data.db
.tables
SELECT * FROM listeners;
.quit
```

## 🔄 Development Workflow

### Making Changes

1. **Edit Python files** → Flask auto-reloads (in debug mode)
2. **Edit frontend files** → Refresh browser to see changes
3. **Edit database models** → May need to delete `app_data.db` to reset schema

### Testing Changes

1. **Run tests manually** using curl commands above
2. **Check browser console** for JavaScript errors
3. **Monitor terminal** for Python errors and logs
4. **Test email notifications** with real email addresses

### Git Workflow

```powershell
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Add local development setup"

# Push to repository
git push origin master
```

## 🚀 Ready for Production

When you're ready to deploy:

1. **Change environment variables** to production values
2. **Set** `FLASK_ENV=production`
3. **Use production SMTP** settings
4. **Deploy** using UptimeRobot guide

## 💡 Pro Tips

### Speed Up Development

1. **Use VS Code Live Server** for frontend development
2. **Keep terminal open** to see logs in real-time
3. **Use browser dev tools** to debug API calls
4. **Test with small search terms** to get quick results

### Useful Commands

```powershell
# Quick restart backend
Ctrl+C  # Stop Flask
python app.py  # Restart Flask

# Reset database (clean slate)
del app_data.db
python app.py  # Will recreate database

# Check if ports are in use
netstat -an | findstr :5000

# Kill process on port 5000 (if needed)
taskkill /F /PID <process_id>
```

### Environment Switching

```powershell
# Development
copy .env.development .env

# Production
copy .env.example .env
# Then edit with production values
```

## 📞 Getting Help

### Check These First
1. **Terminal output** - Look for error messages
2. **Browser console** - Check for JavaScript errors
3. **Environment variables** - Verify .env file is correct
4. **Virtual environment** - Make sure it's activated

### Common Error Solutions
- **Import errors**: Check virtual environment is activated
- **Port conflicts**: Use different port with `FLASK_PORT=5001`
- **Email issues**: Verify Gmail App Password
- **Scraping issues**: Check internet connection and Aucor.com access

---

**Happy debugging!** 🐛→✅ Your local development environment is now ready for testing and development.

## 🎯 Next Steps

Once your local setup is working:
1. Test all functionality thoroughly
2. Add your real auction search terms
3. Verify email notifications work
4. Deploy to production using the UptimeRobot guide
5. Set up monitoring with UptimeRobot

You now have a full development environment where you can safely test changes before deploying to production!
