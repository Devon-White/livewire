"""
Create Subscriber Auth Token API endpoint.
Creates a SignalWire Subscriber Authentication Token for agent login.
"""
from .. import api_bp
from flask import request
from stores.user_store import get_user
import logging
from utils.session_utils import get_session_vars, USER_EMAIL, get_rest_client, get_subscriber_login_status
from utils.api_utils import api_error, api_success, validate_json_request
from utils.signalwire_client import SignalWireAPIError

logger = logging.getLogger(__name__)

@api_bp.route('/api/create_sat', methods=['POST'])
@validate_json_request()
def create_sat():
    """Create a subscriber authentication token (SAT)"""
    # Get session variables
    session_vars = get_session_vars()
    email = session_vars.get('user_email')
    subscriber_ok = get_subscriber_login_status()
    
    # Log relevant session data
    logger.info(f"create_sat called with email={email}, subscriber_ok={subscriber_ok}")
    
    # Verify user is authenticated
    if not email:
        logger.error("No user_email in session")
        return api_error('Not authenticated - No email in session', 401)
    
    # Check user exists in user_store
    user = get_user(email)
    if not user:
        logger.error(f"User {email} not found in user_store")
        # Reset session flag using the utility function
        return api_error('Not authenticated - Email not in user store', 401)
    
    # Check SUBSCRIBER_OK flag
    if not subscriber_ok:
        logger.error(f"SUBSCRIBER_OK flag not set for {email}")
        return api_error('Not authenticated - Not logged in as subscriber', 401)
    
    # Get client from session
    client = get_rest_client()
    if not client:
        return api_error('SignalWire client not initialized', 400)
    
    # Create SAT token
    try:
        token = client.create_subscriber_token(email)
        if not token:
            logger.error("Failed to create subscriber token")
            return api_error('Failed to create subscriber token', 500)
        
        logger.info(f"Created subscriber token for {email}")
        return api_success({'token': token})
        
    except SignalWireAPIError as e:
        logger.exception(f"SignalWire API error: {e.message}")
        return api_error(
            'SignalWire API error', 
            500, 
            log_level='error', 
            details={'message': e.message, 'status_code': e.status_code}
        ) 