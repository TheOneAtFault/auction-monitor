from flask import Flask, request, jsonify
from flask_cors import CORS
from models import Listener, init_database
from scheduler import start_scheduler, run_manual_check
from email_service import email_service
import logging
from email_validator import validate_email, EmailNotValidError
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database
init_database()

# Start the auction scheduler in a separate thread
def start_background_scheduler():
    start_scheduler()

# Start scheduler in background thread
scheduler_thread = threading.Thread(target=start_background_scheduler, daemon=True)
scheduler_thread.start()

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
        check_thread = threading.Thread(target=run_manual_check, daemon=True)
        check_thread.start()
        
        return jsonify({'message': 'Manual auction check started'})
        
    except Exception as e:
        logger.error(f"Error running manual check: {e}")
        return jsonify({'error': 'Internal server error'}), 500

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
    # Production mode - no debug
    app.run(debug=False, host='0.0.0.0', port=5000)
