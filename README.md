# 🎯 Auction Listener - Production Ready

A production-ready real-time auction monitoring system that tracks specific items on live.aucor.com and sends email notifications when matches are found.

## 🚀 Features

- **✅ Production Ready**: Cleaned codebase optimized for deployment
- **🔧 Dual Scraper System**: JavaScript-enabled primary + HTTP fallback scraper
- **⏰ Real-Time Monitoring**: Background scheduler checks for new auctions every 30 minutes
- **📧 Email Notifications**: Instant HTML notifications when items match your search terms
- **🌐 Web Interface**: Easy-to-use Vue.js frontend for managing listeners
- **🎯 Exact Search Matching**: Searches only for your exact terms, no variations
- **🔄 Auto-Failover**: Automatically switches to fallback scraper if primary fails

## 🛠️ Tech Stack

- **Frontend**: Vue.js 3 with Composition API
- **Backend**: Python Flask with Selenium WebDriver
- **Database**: SQLite (production-ready, can upgrade to PostgreSQL)
- **Email**: SMTP with HTML templates (Gmail/Outlook/Yahoo support)
- **Web Scraping**: Selenium Chrome + BeautifulSoup for JavaScript-rendered content
- **Scheduling**: APScheduler for background monitoring

## 📁 Production Structure

```
auction-listener/
├── backend/                 # Production backend
│   ├── app.py              # Main Flask application
│   ├── models.py           # Database models
│   ├── web_scraper.py      # Primary JavaScript scraper (Selenium)
│   ├── fallback_scraper.py # Fallback HTTP scraper
│   ├── email_service.py    # Email notification service
│   ├── scheduler.py        # Background monitoring system
│   ├── manual_test.py      # Production testing utility
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   ├── app_data.db        # SQLite database (auto-created)
│   └── PRODUCTION.md      # Production deployment guide
├── frontend/               # Web interface
│   ├── index.html         # Main HTML application
│   ├── main.js            # Vue.js application logic
│   └── style.css          # Styling
├── README.md              # This file
└── start.bat              # Windows startup script
```

## 🚀 Quick Start

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your email credentials
python app.py
```

### 2. Frontend Access
Open `frontend/index.html` in your web browser or access `http://localhost:5000`

### 3. Production Testing
```bash
python manual_test.py  # Test scraper system
```

## 📋 Usage

1. **Add Listeners**: Enter email address and search terms you want to monitor
2. **Automatic Monitoring**: System checks every 30 minutes for new auction items
3. **Email Alerts**: Receive HTML notifications when matching items are found
4. **Manage Subscriptions**: View, activate/deactivate, or delete listeners via web interface

## ⚙️ Configuration

Create `.env` file in backend directory:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
USE_TLS=true
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

**Gmail Setup**: Use App Password instead of regular password
- Visit: https://support.google.com/accounts/answer/185833

## 🌐 Deployment Options

- **🆓 Free**: Railway.app, Fly.io, Render.com
- **☁️ Cloud**: AWS Africa (Cape Town), Azure SA, DigitalOcean
- **🏠 Self-hosted**: See `PRODUCTION.md` for complete setup guide

## 🔍 Production Features

- ✅ No debug code or test files
- ✅ Production logging levels
- ✅ Error handling and failover
- ✅ Clean, optimized codebase
- ✅ Environment variable configuration
- ✅ Comprehensive documentation

**Ready for production deployment! 🎉**
