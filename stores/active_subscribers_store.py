# active_subscribers_store.py
# Global in-memory store for tracking online subscribers and their addresses, namespaced by project_id only
# Structure: {project_id: {subscriber_id: {address: str, online: bool, last_seen: datetime}}}

from datetime import datetime, UTC
from utils.session_utils import get_session_vars
from flask import session as flask_session
from typing import Dict, Any, Optional
import logging
from . import get_store, ACTIVE_SUBSCRIBERS_STORE, store_operation

logger = logging.getLogger(__name__)

@store_operation
def get_project_key(session_obj=None):
    """
    Extract the project_id from the session for namespacing.
    
    Args:
        session_obj: Optional session object. Uses current Flask session if None.
        
    Returns:
        str: Project ID from session or "global" if not available
    """
    try:
        vars = get_session_vars(session_obj)
        project_id = vars.get('project_id')
        
        if not project_id:
            raise KeyError('project_id must be present in session variables')
            
        return project_id
    except Exception as e:
        # If no session is available or other error, use a fallback namespace key
        # This prevents errors when dealing with beacon/beforeunload requests
        logger.warning(f"Error getting project key from session: {e}")
        return "global"

@store_operation
def get_active_subscribers_store():
    """
    Get the active subscribers store instance.
    
    Returns:
        dict: The active subscribers store instance
    """
    return get_store(ACTIVE_SUBSCRIBERS_STORE)

@store_operation
def set_active_subscriber(subscriber_id, address, session_obj=None):
    """
    Mark a subscriber as active (online) and store their address.
    
    Args:
        subscriber_id (str): The subscriber ID to mark as active
        address (str): The subscriber's address (for call routing)
        session_obj: Optional session object. Uses current Flask session if None.
        
    Returns:
        bool: True if successful
    """
    try:
        # Get namespace key from session
        key = get_project_key(session_obj)
        logger.info(f"Marking subscriber {subscriber_id} as active in project {key}")
        
        # Get the active subscribers store
        active_subscribers = get_active_subscribers_store()
        
        # Initialize project namespace if needed
        if key not in active_subscribers:
            active_subscribers[key] = {}
            
        # Set subscriber as active
        active_subscribers[key][subscriber_id] = {
            'address': address,
            'online': True,
            'last_seen': datetime.now(UTC)
        }
        return True
    except Exception as e:
        logger.exception(f"Error setting active subscriber: {e}")
        return False

@store_operation
def set_inactive_subscriber(subscriber_id, session_obj=None):
    """
    Mark a subscriber as inactive (offline).
    
    Args:
        subscriber_id (str): The subscriber ID to mark as inactive
        session_obj: Optional session object. Uses current Flask session if None.
        
    Returns:
        bool: True if successful, False if subscriber not found
    """
    try:
        # Get namespace key from session
        key = get_project_key(session_obj)
        
        # Get the active subscribers store
        active_subscribers = get_active_subscribers_store()
        
        # If subscriber exists in store, mark as inactive
        if key in active_subscribers and subscriber_id in active_subscribers[key]:
            active_subscribers[key][subscriber_id]['online'] = False
            active_subscribers[key][subscriber_id]['last_seen'] = datetime.now(UTC)
            logger.info(f"Marked subscriber {subscriber_id} as inactive in project {key}")
            return True
        return False
    except Exception as e:
        logger.exception(f"Error setting inactive subscriber: {e}")
        return False

@store_operation
def get_active_subscribers(session_obj=None):
    """
    Get all active subscribers for the current project.
    
    Args:
        session_obj: Optional session object. Uses current Flask session if None.
        
    Returns:
        dict: Dictionary of active subscribers and their data
    """
    try:
        # Get namespace key from session
        key = get_project_key(session_obj)
        
        # Get the active subscribers store
        active_subscribers = get_active_subscribers_store()
        
        # Return only active subscribers for this project
        if key not in active_subscribers:
            return {}
            
        return {k: v for k, v in active_subscribers[key].items() if v.get('online', False)}
    except Exception as e:
        logger.exception(f"Error getting active subscribers: {e}")
        return {}

@store_operation
def get_subscriber_address(subscriber_id, session_obj=None):
    """
    Get the address of a specific subscriber.
    
    Args:
        subscriber_id (str): The subscriber ID to get the address for
        session_obj: Optional session object. Uses current Flask session if None.
        
    Returns:
        str or None: The subscriber's address if found, or None
    """
    try:
        # Get namespace key from session
        key = get_project_key(session_obj)
        
        # Get the active subscribers store
        active_subscribers = get_active_subscribers_store()
        
        # Return address if found
        return active_subscribers.get(key, {}).get(subscriber_id, {}).get('address')
    except Exception as e:
        logger.exception(f"Error getting subscriber address: {e}")
        return None

@store_operation
def get_active_subscribers_by_project(project_id):
    """
    Get all active subscribers for a specific project.
    
    Args:
        project_id (str): The project ID to get subscribers for
        
    Returns:
        dict: Dictionary of active subscribers and their data
    """
    try:
        # Get the active subscribers store
        active_subscribers = get_active_subscribers_store()
        
        # Return only active subscribers for this project
        if project_id not in active_subscribers:
            return {}
            
        return {k: v for k, v in active_subscribers[project_id].items() if v.get('online', False)}
    except Exception as e:
        logger.exception(f"Error getting active subscribers by project: {e}")
        return {} 