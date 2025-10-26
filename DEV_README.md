# 🛠️ Local Development - Quick Start

## ⚡ Super Quick Setup (1 minute)

1. **Double-click** `start_dev.bat` 
2. **Edit** `.env` file with your Gmail credentials
3. **Restart** the script
4. **Open** `frontend/index.html` in your browser

## 🧪 Test Everything

**Run tests**: Double-click `test_local.bat` or run:
```bash
python test_local.py
```

## 🔧 Manual Testing

**Test individual endpoints**:
```bash
# Health check
curl http://localhost:5000/

# Get stats
curl http://localhost:5000/api/stats

# Trigger auction check
curl http://localhost:5000/cron/local-development-secret-key

# Send test email
curl -X POST "http://localhost:5000/api/test-email" -H "Content-Type: application/json" -d "{\"email\":\"your@email.com\"}"
```

## 🐛 Debugging

### VS Code Debugging
1. **Install Python extension**
2. **Press F5** to start debugging
3. **Set breakpoints** in Python code

### View Logs
- Check the terminal where you run `python backend/app.py`
- Look for emoji indicators: 🔧 📧 📦 ✅ ❌

### Common Issues
- **Import errors**: Make sure virtual environment is activated
- **Email not working**: Check Gmail App Password (16 characters)
- **Port in use**: Kill process or use different port
- **CORS errors**: Make sure backend is on localhost:5000

## 🔄 Reset Everything

**Clean slate**: Double-click `reset_dev.bat`

## 📁 File Structure

```
auction-monitor/
├── backend/           # Python Flask API
│   ├── app.py        # Main application
│   ├── models.py     # Database models
│   └── .env          # Your environment variables
├── frontend/         # Vue.js web interface
│   └── index.html    # Open this in browser
├── start_dev.bat     # Start development server
├── test_local.bat    # Test all functionality
└── reset_dev.bat     # Reset everything
```

## 🎯 Development Workflow

1. **Start backend**: `start_dev.bat`
2. **Open frontend**: `frontend/index.html` in browser
3. **Make changes** to Python or frontend code
4. **Test changes** with `test_local.bat`
5. **Commit changes** when ready

## 🚀 Ready for Production?

Follow the **UptimeRobot Guide** to deploy your working application!
