from flask import Flask, request, jsonify
from flask_cors import CORS
from models import Listener, init_database
from email_service import email_service
import logging
from email_validator import validate_email, EmailNotValidError
import threading
import os
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database
init_database()

# UptimeRobot trigger configuration
UPTIMEROBOT_SECRET = os.getenv('UPTIMEROBOT_SECRET', 'your-secret-key-here')

def run_auction_check():
    """Run auction check (same logic as scheduler but for HTTP trigger)"""
    try:
        logger.info("🚀 Starting UptimeRobot triggered auction check...")
        
        # Import here to avoid circular imports and allow optional selenium
        try:
            from web_scraper import WebScraper
            scraper = WebScraper()
            logger.info("✅ Using Selenium web scraper")
        except ImportError:
            from fallback_scraper import FallbackScraper
            scraper = FallbackScraper()
            logger.info("⚠️ Using fallback scraper (Selenium not available)")
        
        # Get new auction items
        new_items = scraper.get_new_items()
        
        if not new_items:
            logger.info("ℹ️ No new auction items found")
            return {'status': 'success', 'message': 'No new items found', 'items_found': 0}
        
        # Get all active listeners
        listeners = Listener.get_all()
        
        if not listeners:
            logger.info("ℹ️ No active listeners found")
            return {'status': 'success', 'message': 'No listeners configured', 'items_found': len(new_items)}
        
        # Check each new item against each listener's search terms
        notifications_sent = 0
        
        from fallback_scraper import match_search_terms
        from models import Notification
        
        for item in new_items:
            # Get all unique search terms from listeners
            search_terms = [listener.search_term for listener in listeners]
            
            # Check if this item matches any search terms
            matching_terms = match_search_terms(item, search_terms)
            
            if matching_terms:
                logger.info(f"📦 Item '{item.title}' matches terms: {matching_terms}")
                
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
                                logger.info(f"📧 Notification sent to {listener.email} for '{item.title}'")
                            else:
                                logger.error(f"❌ Failed to send notification to {listener.email}")
        
        # Clean up scraper
        if hasattr(scraper, 'close'):
            scraper.close()
        
        result = {
            'status': 'success',
            'message': f'Check completed. {notifications_sent} notifications sent.',
            'items_found': len(new_items),
            'notifications_sent': notifications_sent
        }
        
        logger.info(f"✅ Auction check completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error during auction check: {e}")
        return {'status': 'error', 'message': str(e), 'items_found': 0}

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'message': 'Aucor Auction Listener API is running'
    })

@app.route('/api/listeners', methods=['POST'])
def add_listener():
    """Add a new auction listener"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        search_term = data.get('search_term', '').strip()
        
        # Validate input
        if not email or not search_term:
            return jsonify({'error': 'Email and search term are required'}), 400
        
        # Validate email format
        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate search term length
        if len(search_term) < 2:
            return jsonify({'error': 'Search term must be at least 2 characters long'}), 400
        
        # Create and save listener
        listener = Listener(email=email, search_term=search_term)
        
        if listener.save():
            logger.info(f"New listener added: {email} for term '{search_term}'")
            return jsonify({
                'message': 'Listener added successfully',
                'listener': {
                    'id': listener.id,
                    'email': listener.email,
                    'search_term': listener.search_term
                }
            }), 201
        else:
            return jsonify({'error': 'This email and search term combination already exists'}), 409
            
    except Exception as e:
        logger.error(f"Error adding listener: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/listeners/<email>', methods=['GET'])
def get_listeners(email):
    """Get all listeners for a specific email"""
    try:
        # Validate email format
        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({'error': 'Invalid email format'}), 400
        
        listeners = Listener.get_by_email(email)
        
        listeners_data = []
        for listener in listeners:
            listeners_data.append({
                'id': listener.id,
                'email': listener.email,
                'search_term': listener.search_term,
                'created_at': listener.created_at,
                'active': listener.active
            })
        
        return jsonify({'listeners': listeners_data})
        
    except Exception as e:
        logger.error(f"Error retrieving listeners: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/listeners/<int:listener_id>', methods=['DELETE'])
def delete_listener(listener_id):
    """Delete a specific listener"""
    try:
        if Listener.delete(listener_id):
            logger.info(f"Listener {listener_id} deleted")
            return jsonify({'message': 'Listener deleted successfully'})
        else:
            return jsonify({'error': 'Listener not found'}), 404
            
    except Exception as e:
        logger.error(f"Error deleting listener: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Send a test email to verify email configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        
        # Validate email format
        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Send test email
        if email_service.send_test_email(email):
            return jsonify({'message': 'Test email sent successfully'})
        else:
            return jsonify({'error': 'Failed to send test email'}), 500
            
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/manual-check', methods=['POST'])
def manual_check():
    """Manually trigger an auction check"""
    try:
        # Run manual check in background thread to avoid blocking
        check_thread = threading.Thread(target=lambda: run_auction_check(), daemon=True)
        check_thread.start()
        
        return jsonify({'message': 'Manual auction check started'})
        
    except Exception as e:
        logger.error(f"Error running manual check: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/cron/<secret_key>', methods=['GET', 'POST'])
def uptimerobot_trigger(secret_key):
    """UptimeRobot endpoint to trigger auction checking"""
    try:
        # Verify secret key for security
        if secret_key != UPTIMEROBOT_SECRET:
            logger.warning(f"❌ Invalid secret key attempt: {secret_key}")
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Log the trigger
        logger.info(f"🤖 UptimeRobot trigger received at {datetime.now()}")
        
        # Run auction check synchronously for UptimeRobot
        result = run_auction_check()
        
        # Return detailed response for monitoring
        return jsonify({
            'trigger': 'uptimerobot',
            'timestamp': datetime.now().isoformat(),
            'result': result
        })
        
    except Exception as e:
        logger.error(f"❌ Error in UptimeRobot trigger: {e}")
        return jsonify({
            'trigger': 'uptimerobot',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@app.route('/cron-status/<secret_key>', methods=['GET'])
def cron_status(secret_key):
    """Check cron job status and system health"""
    try:
        # Verify secret key
        if secret_key != UPTIMEROBOT_SECRET:
            return jsonify({'error': 'Unauthorized'}), 401
        
        listeners = Listener.get_all()
        
        # Get recent notifications count (if we can)
        try:
            from models import AuctionItem
            recent_items = AuctionItem.get_all()
            recent_items_count = len([item for item in recent_items if item.scraped_at])
        except:
            recent_items_count = 0
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'listeners_count': len(listeners),
            'recent_items_scraped': recent_items_count,
            'secret_key_valid': True
        })
        
    except Exception as e:
        logger.error(f"Error in cron status: {e}")
        return jsonify({
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get basic statistics about the system"""
    try:
        listeners = Listener.get_all()
        
        stats = {
            'total_listeners': len(listeners),
            'unique_emails': len(set(listener.email for listener in listeners)),
            'search_terms': [listener.search_term for listener in listeners]
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Check if running in development mode
    debug_mode = os.getenv('FLASK_ENV', 'production') == 'development'
    host = os.getenv('FLASK_HOST', '127.0.0.1' if debug_mode else '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    if debug_mode:
        logger.info("🔧 Starting in DEVELOPMENT mode")
        logger.info(f"📡 Server will be available at: http://{host}:{port}")
        logger.info("🌐 Frontend should use: http://localhost:5000/api")
    else:
        logger.info("🚀 Starting in PRODUCTION mode")
    
    app.run(debug=debug_mode, host=host, port=port)
