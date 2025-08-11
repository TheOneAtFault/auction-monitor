from apscheduler.schedulers.background import BackgroundScheduler
from fallback_scraper import FallbackScraper, match_search_terms
from models import Listener, Notification
from email_service import email_service
import logging
import atexit

# Try to import web scraper, fall back to basic scraper if not available
try:
    from web_scraper import WebScraper
    WEB_SCRAPER_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ Web scraper available - will use JavaScript rendering")
except ImportError as e:
    WEB_SCRAPER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ Selenium not available, using basic scraper: {e}")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuctionScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        # Use web scraper if available, otherwise fall back to basic scraper
        if WEB_SCRAPER_AVAILABLE:
            logger.info("🚀 Initializing with web scraper (JavaScript enabled)")
            self.scraper = WebScraper()
        else:
            logger.info("📄 Initializing with fallback scraper (basic HTTP)")
            self.scraper = FallbackScraper()
        
        # Schedule the auction checking job to run every 30 minutes
        self.scheduler.add_job(
            func=self.check_auctions,
            trigger="interval",
            minutes=30,
            id='auction_checker',
            name='Check for new auction items'
        )
        
        # Also run a job every hour to clean up old data if needed
        self.scheduler.add_job(
            func=self.cleanup_old_data,
            trigger="interval",
            hours=24,
            id='cleanup_job',
            name='Clean up old auction data'
        )
    
    def start(self):
        """Start the scheduler"""
        try:
            self.scheduler.start()
            logger.info("Auction scheduler started successfully")
            
            # Register shutdown handler
            atexit.register(lambda: self.scheduler.shutdown())
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Auction scheduler stopped")
    
    def check_auctions(self):
        """Main job function - check for new auctions and send notifications"""
        logger.info("Starting auction check...")
        
        try:
            # Get new auction items
            new_items = self.scraper.get_new_items()
            
            if not new_items:
                logger.info("No new auction items found")
                return
            
            # Get all active listeners
            listeners = Listener.get_all()
            
            if not listeners:
                logger.info("No active listeners found")
                return
            
            # Check each new item against each listener's search terms
            notifications_sent = 0
            
            for item in new_items:
                # Get all unique search terms from listeners
                search_terms = [listener.search_term for listener in listeners]
                
                # Check if this item matches any search terms
                matching_terms = match_search_terms(item, search_terms)
                
                if matching_terms:
                    logger.info(f"Item '{item.title}' matches terms: {matching_terms}")
                    
                    # Send notifications to relevant listeners
                    for listener in listeners:
                        if listener.search_term in matching_terms:
                            # Check if we've already sent a notification for this combination
                            if not Notification.already_sent(listener.id, item.id):
                                # Send email notification
                                if email_service.send_notification(
                                    listener.email, 
                                    item, 
                                    listener.search_term
                                ):
                                    # Record the notification
                                    Notification.save(listener.id, item.id)
                                    notifications_sent += 1
                                    logger.info(f"Notification sent to {listener.email} for '{item.title}'")
                                else:
                                    logger.error(f"Failed to send notification to {listener.email}")
            
            logger.info(f"Auction check completed. {notifications_sent} notifications sent.")
            
        except Exception as e:
            logger.error(f"Error during auction check: {e}")
    
    def cleanup_old_data(self):
        """Clean up old auction data (optional maintenance job)"""
        logger.info("Running cleanup job...")
        # This could be expanded to remove old auction items, notifications, etc.
        # For now, we'll just log that it ran
        logger.info("Cleanup job completed")
    
    def run_immediate_check(self):
        """Run an immediate auction check (useful for testing)"""
        logger.info("Running immediate auction check...")
        self.check_auctions()

# Create global scheduler instance
auction_scheduler = AuctionScheduler()

def start_scheduler():
    """Start the auction scheduler"""
    auction_scheduler.start()

def stop_scheduler():
    """Stop the auction scheduler"""
    auction_scheduler.stop()

def run_manual_check():
    """Run a manual check"""
    auction_scheduler.run_immediate_check()
