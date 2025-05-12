"""
User store module.
Manages user authentication data and subscriber mapping.
"""

import logging
from typing import Any, Dict, Optional

from werkzeug.security import generate_password_hash

from . import USER_STORE, get_store, store_operation

logger = logging.getLogger(__name__)


@store_operation
def _initialize_store() -> Dict[str, Dict[str, Any]]:
    """
    Initialize the user store with sample data for testing.

    Returns:
        Dict[str, Dict[str, Any]]: The user store instance
    """
    store = get_store(USER_STORE)

    # Only add sample user if store is empty
    if not store:
        # Sample user for testing - email: test@example.com, password: testpassword
        store["test@example.com"] = {
            "password_hash": generate_password_hash("testpassword"),
            "subscriber_id": "test-subscriber-id",
            "display_name": "Test User",
            "first_name": "Test",
            "last_name": "User",
        }
        logger.info("Initialized user store with sample test user: test@example.com")

    return store


@store_operation
def get_user_store() -> Dict[str, Dict[str, Any]]:
    """
    Get the user store instance.

    Returns:
        Dict[str, Dict[str, Any]]: The user store instance
    """
    return _initialize_store()


@store_operation
def get_user(email: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by email.

    Args:
        email (str): Email address to look up (case-insensitive)

    Returns:
        Optional[Dict[str, Any]]: User data if found, None otherwise
    """
    store = get_user_store()
    return store.get(email.lower())
