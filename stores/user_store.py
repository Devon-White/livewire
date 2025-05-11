"""
User store module.
Manages user authentication data and subscriber mapping.
"""
from . import get_store, USER_STORE, store_operation
from werkzeug.security import generate_password_hash
import logging

logger = logging.getLogger(__name__)

def _initialize_store():
    """
    Initialize the user store with sample data for testing.
    
    Returns:
        dict: The user store instance
    """
    store = get_store(USER_STORE)
    
    # Only add sample user if store is empty
    if not store:
        # Sample user for testing - email: test@example.com, password: testpassword
        store['test@example.com'] = {
            'password_hash': generate_password_hash('testpassword'),
            'subscriber_id': 'test-subscriber-id',
            'display_name': 'Test User',
            'first_name': 'Test',
            'last_name': 'User'
        }
        logger.info("Initialized user store with sample test user: test@example.com")
    
    return store

@store_operation
def get_user_store():
    """
    Get the user store instance.
    
    Returns:
        dict: The user store instance
    """
    return _initialize_store()

@store_operation
def get_user(email):
    """
    Get a user by email.
    
    Args:
        email (str): Email address to look up (case-insensitive)
        
    Returns:
        dict or None: User data if found, None otherwise
    """
    store = get_user_store()
    return store.get(email.lower()) 