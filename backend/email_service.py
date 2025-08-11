import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Email configuration - you can set these as environment variables
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', 'your-email@gmail.com')
        self.sender_password = os.getenv('SENDER_PASSWORD', 'your-app-password')
        self.use_tls = os.getenv('USE_TLS', 'true').lower() == 'true'
    
    def send_notification(self, recipient_email, auction_item, search_term):
        """Send auction notification email"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"🔔 Auction Alert: {search_term} - {auction_item.title}"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Create HTML content
            html_content = self._create_html_email(auction_item, search_term)
            
            # Create plain text content
            text_content = self._create_text_email(auction_item, search_term)
            
            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            
            # Add HTML/plain-text parts to MIMEMultipart message
            message.attach(part1)
            message.attach(part2)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            logger.info(f"Notification sent to {recipient_email} for item: {auction_item.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {e}")
            logger.error(f"SMTP Details - Server: {self.smtp_server}:{self.smtp_port}, TLS: {self.use_tls}, From: {self.sender_email}")
            return False
    
    def _create_html_email(self, auction_item, search_term):
        """Create HTML email content"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border: 1px solid #ddd;
                }}
                .auction-item {{
                    background-color: white;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;
                    border-left: 4px solid #4CAF50;
                }}
                .btn {{
                    display: inline-block;
                    background-color: #4CAF50;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 4px;
                    margin: 10px 0;
                }}
                .btn:hover {{
                    background-color: #45a049;
                }}
                .footer {{
                    background-color: #333;
                    color: white;
                    padding: 15px;
                    text-align: center;
                    font-size: 12px;
                    border-radius: 0 0 8px 8px;
                }}
                .search-term {{
                    background-color: #e7f3ff;
                    padding: 5px 10px;
                    border-radius: 4px;
                    display: inline-block;
                    font-weight: bold;
                    color: #0066cc;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔔 Auction Alert!</h1>
                <p>We found a match for your search term: <span class="search-term">{search_term}</span></p>
            </div>
            
            <div class="content">
                <div class="auction-item">
                    <h2>{auction_item.title}</h2>
                    
                    {f'<img src="{auction_item.image_url}" alt="Auction Item" style="max-width: 100%; height: auto; border-radius: 4px; margin: 10px 0;">' if auction_item.image_url else ''}
                    
                    {f'<p><strong>Description:</strong> {auction_item.description}</p>' if auction_item.description else ''}
                    
                    {f'<p><strong>Current Price:</strong> {auction_item.price}</p>' if auction_item.price else ''}
                    
                    {f'<p><strong>End Time:</strong> {auction_item.end_time}</p>' if auction_item.end_time else ''}
                    
                    <a href="{auction_item.url}" class="btn" target="_blank">View Auction Item</a>
                </div>
                
                <p><strong>Why you received this:</strong> This auction item matches your search term "<strong>{search_term}</strong>" that you're monitoring.</p>
                
                <p><em>Don't miss out! Click the link above to view the full auction details and place your bid.</em></p>
            </div>
            
            <div class="footer">
                <p>Aucor Auction Listener - Automated Auction Monitoring</p>
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
    
    def _create_text_email(self, auction_item, search_term):
        """Create plain text email content"""
        return f"""
🔔 AUCTION ALERT!

We found a match for your search term: {search_term}

AUCTION ITEM DETAILS:
Title: {auction_item.title}

{f'Description: {auction_item.description}' if auction_item.description else ''}

{f'Current Price: {auction_item.price}' if auction_item.price else ''}

{f'End Time: {auction_item.end_time}' if auction_item.end_time else ''}

VIEW AUCTION: {auction_item.url}

Why you received this: This auction item matches your search term "{search_term}" that you're monitoring.

Don't miss out! Visit the link above to view the full auction details and place your bid.

---
Aucor Auction Listener - Automated Auction Monitoring
This is an automated message. Please do not reply to this email.
        """
    
    def send_test_email(self, recipient_email):
        """Send a test email to verify email configuration"""
        try:
            message = MIMEText("This is a test email from Aucor Auction Listener. Your email configuration is working correctly!")
            message["Subject"] = "Test Email - Aucor Auction Listener"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            logger.info(f"Test email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send test email to {recipient_email}: {e}")
            logger.error(f"SMTP Details - Server: {self.smtp_server}:{self.smtp_port}, TLS: {self.use_tls}, From: {self.sender_email}")
            return False

# Create a global instance
email_service = EmailService()
