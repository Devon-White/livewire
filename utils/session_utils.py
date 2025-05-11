"""
Session utility functions for the LiveWire demo app.
Provides consistent access to session variables and common operations.
"""
from flask import session as flask_session
import logging

logger = logging.getLogger(__name__)

# Session key constants
SW_PROJECT_ID = 'sw_project_id'
SW_AUTH_TOKEN = 'sw_auth_token'
SW_SPACE_NAME = 'sw_space_name'
SW_CREDENTIALS_OK = 'sw_credentials_ok'
SUBSCRIBER_OK = 'subscriber_ok'
SWML_ID = 'swml_id'
SWML_DESTINATION = 'swml_destination'
CURRENT_CALL_ID = 'current_call_id'
USER_EMAIL = 'user_email'

def get_session_vars(session_obj=None):
    """
    Returns a dict of all relevant session variables for namespacing data.
    
    Args:
        session_obj: Optional session object to use instead of flask.session
        
    Returns:
        dict: Dictionary of session variables
    """
    s = session_obj if session_obj is not None else flask_session
    
    # Always log what's in the session for debugging
    logger.debug(f"Session keys: {list(s.keys())}")
    logger.debug(f"Project ID: {s.get(SW_PROJECT_ID)}")
    logger.debug(f"Space Name: {s.get(SW_SPACE_NAME)}")
    logger.debug(f"Credentials OK: {s.get(SW_CREDENTIALS_OK)}")
    
    return {
        'project_id': s.get(SW_PROJECT_ID),
        'auth_token': s.get(SW_AUTH_TOKEN),
        'space_name': s.get(SW_SPACE_NAME),
        'swml_id': s.get(SWML_ID),
        'swml_destination': s.get(SWML_DESTINATION),
        'current_call_id': s.get(CURRENT_CALL_ID),
        'user_email': s.get(USER_EMAIL),
    }

def has_sw_credentials():
    """
    Check if SignalWire credentials are present in the session.
    Always verifies the actual credentials, not just the flag.
    """
    # Check both the flag AND all credential values
    flag_set = bool(flask_session.get(SW_CREDENTIALS_OK))
    project_id = bool(flask_session.get(SW_PROJECT_ID))
    auth_token = bool(flask_session.get(SW_AUTH_TOKEN))
    space_name = bool(flask_session.get(SW_SPACE_NAME))
    
    # Log the state for debugging
    logger.debug(f"Credential check: flag={flag_set}, project={project_id}, auth={auth_token}, space={space_name}")
    
    # All must be present
    return flag_set and project_id and auth_token and space_name

def is_subscriber_logged_in():
    """
    Check if user is logged in as a subscriber.
    Verifies both the flag and the email.
    """
    flag_set = bool(flask_session.get(SUBSCRIBER_OK))
    has_email = bool(flask_session.get(USER_EMAIL))
    
    logger.debug(f"Subscriber check: flag={flag_set}, email={has_email}")
    
    return flag_set and has_email

def get_subscriber_login_status():
    """
    Get the subscriber login status flag from the session.
    
    Returns:
        bool: True if subscriber_ok flag is set, False otherwise
    """
    status = bool(flask_session.get(SUBSCRIBER_OK, False))
    logger.debug(f"Getting subscriber login status: {status}")
    return status

def set_sw_credentials(project_id, auth_token, space_name):
    """
    Store SignalWire credentials in the session.
    All values must be non-empty.
    """
    if not (project_id and auth_token and space_name):
        logger.warning("Attempted to set empty credentials")
        return False
        
    flask_session[SW_PROJECT_ID] = project_id
    flask_session[SW_AUTH_TOKEN] = auth_token
    flask_session[SW_SPACE_NAME] = space_name
    flask_session[SW_CREDENTIALS_OK] = True
    
    logger.info(f"Set credentials for project {project_id}, space {space_name}")
    return True

def get_rest_client():
    """
    Create a SignalWireClient instance using credentials from the session.
    The client is created fresh each time to avoid serialization issues.
    
    Returns:
        SignalWireClient or None: The client instance or None if credentials are missing
    """
    # Import here to avoid circular imports
    from utils.signalwire_client import SignalWireClient
    
    # Check if we have credentials to create a client
    if not has_sw_credentials():
        logger.warning("Cannot create SignalWireClient - missing credentials")
        return None
    
    # Get credentials and create a new client
    project_id = flask_session.get(SW_PROJECT_ID)
    auth_token = flask_session.get(SW_AUTH_TOKEN)
    space_name = flask_session.get(SW_SPACE_NAME)
    
    # Create the client (but don't store it in the session)
    client = SignalWireClient(project_id, auth_token, space_name)
    logger.debug(f"Created new SignalWireClient for {project_id} in {space_name}")
    
    return client
    
def set_subscriber_login(email):
    """Mark user as logged in as a subscriber"""
    if not email:
        logger.warning("Attempted to set empty subscriber email")
        return False
        
    flask_session[USER_EMAIL] = email
    flask_session[SUBSCRIBER_OK] = True
    
    logger.info(f"Set subscriber login for {email}")
    return True

def clear_subscriber_login():
    """
    Clear only the subscriber login information from the session,
    preserving other session data like SignalWire credentials.
    
    Returns:
        bool: True if successful
    """
    flask_session.pop(SUBSCRIBER_OK, None)
    flask_session.pop(USER_EMAIL, None)
    
    logger.info("Cleared subscriber login information")
    return True

def set_swml_handler_info(handler_id, destination=None):
    """
    Store SWML handler information in the session.
    
    Args:
        handler_id: The SWML handler ID
        destination: Optional destination URL
    """
    if not handler_id:
        logger.warning("Attempted to set empty SWML handler ID")
        return False
        
    flask_session[SWML_ID] = handler_id
    if destination:
        flask_session[SWML_DESTINATION] = destination
    
    logger.info(f"Set SWML handler info: ID={handler_id}, destination={destination or 'None'}")
    return True

def set_current_call_id(call_id):
    """
    Store the current call ID in the session.
    
    Args:
        call_id: Active call ID
    """
    if not call_id:
        logger.warning("Attempted to set empty call ID")
        return False
        
    flask_session[CURRENT_CALL_ID] = call_id
    logger.info(f"Set current call ID: {call_id}")
    return True

def get_current_call_id():
    """
    Get the current call ID from the session.
    
    Returns:
        str: The current call ID or None if not set
    """
    call_id = flask_session.get(CURRENT_CALL_ID)
    return call_id
    
def clear_session():
    """
    Clear all session data and ensure nothing remains.
    """
    # Log what we're clearing
    logger.info(f"Clearing session with keys: {list(flask_session.keys())}")
    
    # Clear everything
    flask_session.clear()
    
    # Verify it's actually cleared
    logger.info(f"Session after clearing: {list(flask_session.keys())}")
    
    return True 