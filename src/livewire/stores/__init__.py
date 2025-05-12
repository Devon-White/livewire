# stores/__init__.py
"""
Store module for LiveWire demo app.
Provides a consistent interface for in-memory stores used throughout the application.
"""
import logging
import os
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)

# Define standard store names to prevent typos and ensure consistency
CUSTOMER_STORE: str = "customers"
CALL_INFO_STORE: str = "call_info"
USER_STORE: str = "users"
ACTIVE_SUBSCRIBERS_STORE: str = "active_subscribers"

# Store registry to track all stores in the application
_stores: Dict[str, Dict[str, Any]] = {}


def get_store(store_name: str) -> Dict[str, Any]:
    """
    Get or create an in-memory store by name.
    Returns the same dictionary instance for a given name across the application.

    Args:
        store_name (str): Name of the store to get or create

    Returns:
        Dict[str, Any]: The in-memory store instance
    """
    if store_name not in _stores:
        _stores[store_name] = {}
        logger.debug(f"Created new store: {store_name}")
    return _stores[store_name]


# Simple decorator for error handling in store operations
def store_operation(func: Callable) -> Callable:
    """
    Simple decorator for consistent error handling in store operations.
    Logs exceptions but allows them to propagate.

    Args:
        func (Callable): The store operation function to decorate

    Returns:
        Callable: The decorated function
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in store operation {func.__name__}: {e}")
            raise

    return wrapper
