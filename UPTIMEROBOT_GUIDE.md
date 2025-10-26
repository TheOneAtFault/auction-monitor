# 🚀 UptimeRobot + Shared Hosting Deployment Guide

This guide shows you how to deploy your auction monitor using **UptimeRobot** as a cron service to trigger auction checks, perfect for shared hosting!

## 🎯 **How This Works**

Instead of running background schedulers (which shared hosting doesn't support), we use:

1. **Your Flask app** runs on shared hosting or cloud service
2. **UptimeRobot** hits a special endpoint every 30 minutes
3. **The endpoint** triggers auction scraping and email notifications
4. **Everything works** without background processes!

## 📋 **Architecture Overview**

```
UptimeRobot (Free) 
    ↓ (every 30 minutes)
    GET https://yourdomain.com/cron/your-secret-key
    ↓
Your Flask App (Shared Hosting/Cloud)
    ↓
Scrapes Aucor + Sends Emails
```

## 🔧 **Step 1: Deploy Your Flask App**

### Option A: Shared Hosting with Python Support

**Check if Afrihost supports Python**:
- Call: 087 470 0000
- Ask: "Do you support Python Flask applications?"
- If YES: Upload your `backend` folder to their servers
- If NO: Use Option B

### Option B: Cloud Hosting (Recommended)

**Railway.app** (Easiest):
1. Create account: https://railway.app
2. Connect your GitHub repository
3. Deploy the `backend` folder
4. Set environment variables:
   ```
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-16-char-app-password
   UPTIMEROBOT_SECRET=generate-random-key-here
   ```
5. Get your app URL: `https://your-app.railway.app`

**Other Cloud Options**:
- **Render.com**: Free tier with sleep (perfect for this use case)
- **Heroku**: $7/month, very reliable
- **PythonAnywhere**: $5/month, Python-focused

## 🔐 **Step 2: Generate Secret Key**

For security, generate a random secret key:

```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(f"Your secret key: {secret_key}")
```

Set this as `UPTIMEROBOT_SECRET` in your environment variables.

## 🤖 **Step 3: Set Up UptimeRobot**

### Create UptimeRobot Account
1. Go to: https://uptimerobot.com
2. Create free account (50 monitors free!)
3. Verify your email

### Add Monitor
1. Click "Add New Monitor"
2. **Monitor Type**: HTTP(s)
3. **Friendly Name**: "Auction Monitor Cron"
4. **URL**: `https://your-app-url.com/cron/your-secret-key`
5. **Monitoring Interval**: 30 minutes
6. **Monitor Timeout**: 30 seconds
7. Click "Create Monitor"

### Set Up Alerts (Optional)
1. Go to "Alert Contacts"
2. Add your email for downtime notifications
3. UptimeRobot will email you if your cron job fails

## 📧 **Step 4: Email Configuration**

Set up Gmail App Password:
1. Enable 2-Factor Authentication
2. Go to: https://security.google.com/settings/security/apppasswords
3. Create app password for "Mail"
4. Use in your environment variables

## 🌐 **Step 5: Frontend (Optional)**

You can still host your Vue.js frontend on Afrihost shared hosting:

1. Upload `frontend` files to `public_html`
2. Update `main.js` to point to your cloud-hosted API
3. Users can still add/manage listeners via web interface

## ✅ **Testing Your Setup**

### Test the Cron Endpoint
```bash
# Replace with your actual URL and secret
curl "https://your-app.railway.app/cron/your-secret-key"
```

**Expected Response**:
```json
{
    "trigger": "uptimerobot",
    "timestamp": "2025-10-26T10:30:00",
    "result": {
        "status": "success",
        "message": "Check completed. 0 notifications sent.",
        "items_found": 0,
        "notifications_sent": 0
    }
}
```

### Check Status Endpoint
```bash
curl "https://your-app.railway.app/cron-status/your-secret-key"
```

### Monitor UptimeRobot Dashboard
- Check that your monitor shows "Up"
- Review response times
- Check for any failed requests

## 💰 **Cost Breakdown**

### Free Option
- **UptimeRobot**: Free (50 monitors)
- **Render.com**: Free tier (sleeps after 15min, but UptimeRobot wakes it up!)
- **Gmail**: Free
- **Total**: R0/month 🎉

### Paid Option (More Reliable)
- **UptimeRobot**: Free
- **Railway.app**: $5/month (~R90)
- **Domain**: R25/month
- **Total**: ~R115/month

### With Afrihost Frontend
- **UptimeRobot**: Free
- **Railway.app**: R90/month
- **Afrihost Hosting**: R100/month (for frontend)
- **Domain**: R25/month
- **Total**: ~R215/month

## 🚨 **Troubleshooting**

### Common Issues

**1. UptimeRobot shows "Down"**
- Check your secret key is correct
- Verify your app is running
- Check app logs for errors

**2. No Emails Being Sent**
- Test email endpoint: `POST /api/test-email`
- Check Gmail app password
- Verify SMTP settings

**3. Scraping Not Working**
- Check if Selenium is available
- Test fallback scraper
- Check Aucor.com accessibility

**4. "Unauthorized" Error**
- Verify secret key matches environment variable
- Check environment variables are set correctly

### Useful Commands

```bash
# Check if your app is running
curl https://your-app.railway.app/

# Test cron endpoint
curl "https://your-app.railway.app/cron/your-secret-key"

# Check status
curl "https://your-app.railway.app/cron-status/your-secret-key"

# View logs (Railway)
railway logs

# Test email sending
curl -X POST "https://your-app.railway.app/api/test-email" \
  -H "Content-Type: application/json" \
  -d '{"email":"your-email@gmail.com"}'
```

## 📊 **Monitoring & Maintenance**

### UptimeRobot Dashboard
- Check uptime percentage
- Monitor response times
- Review error logs

### Application Logs
- Monitor for scraping errors
- Check email sending success
- Watch for database issues

### Regular Maintenance
- Check Gmail app password hasn't expired
- Verify auction listeners are still relevant
- Monitor cloud service costs

## 🎯 **Advantages of This Approach**

✅ **Works on any hosting** - No background processes needed  
✅ **Free monitoring** - UptimeRobot handles the scheduling  
✅ **Reliable** - If your app goes down, UptimeRobot alerts you  
✅ **Scalable** - Easy to change timing or add more endpoints  
✅ **Simple** - No complex schedulers or cron jobs  
✅ **Debuggable** - Easy to test and monitor  

## 🚀 **Quick Start Checklist**

- [ ] Deploy Flask app to Railway/Render
- [ ] Set environment variables (email + secret key)
- [ ] Test app endpoints manually
- [ ] Create UptimeRobot account
- [ ] Add monitor with cron endpoint
- [ ] Wait 30 minutes and check logs
- [ ] Add test listener and verify emails work
- [ ] Set up alerting in UptimeRobot

## 📞 **Support**

### UptimeRobot
- **Help**: https://uptimerobot.com/help/
- **Status**: https://status.uptimerobot.com/

### Cloud Providers
- **Railway**: https://docs.railway.app/
- **Render**: https://render.com/docs

### Email Issues
- **Gmail Help**: https://support.google.com/mail/

---

**That's it!** Your auction monitor now runs completely automatically, triggered by UptimeRobot every 30 minutes, and works perfectly with shared hosting! 🎉
