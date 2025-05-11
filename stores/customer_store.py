# customer_store.py
# Global in-memory store for customer/member data
# Structure: {member_id: {first_name, last_name, email, phone, premium_member, ...}}

"""
Customer/member store module.
Provides functions to access and manipulate customer data.
Structure: {member_id: {first_name, last_name, email, phone, premium_member, ...}}
"""
from typing import Dict, Any, Optional, List
from . import get_store, CUSTOMER_STORE, store_operation
import logging

logger = logging.getLogger(__name__)

def _initialize_store() -> Dict[str, Dict[str, Any]]:
    """
    Initialize the customer store with sample data for testing.
    
    Returns:
        Dict: The customer store instance
    """
    store = get_store(CUSTOMER_STORE)
    # Add sample customer only if store is empty
    if not store:
        store["AB12345"] = {
            "member_id": "AB12345",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "premium_member": True
        }
        logger.info("Initialized customer store with sample customer: AB12345")
    return store

@store_operation
def get_customer_store() -> Dict[str, Dict[str, Any]]:
    """
    Get the customer store instance.
    
    Returns:
        Dict: The customer store instance
    """
    return _initialize_store()

@store_operation
def get_customer(member_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific customer by member ID (case-insensitive).
    
    Args:
        member_id (str): The member ID to look up
        
    Returns:
        Dict or None: Customer data if found, None otherwise
    """
    store = get_customer_store()
    
    # Case-insensitive lookup
    for cid, customer in store.items():
        if cid.lower() == member_id.lower():
            return customer
    return None

@store_operation
def add_customer(member_data: Dict[str, Any]) -> bool:
    """
    Add a new customer to the store.
    
    Args:
        member_data (Dict): Customer data including member_id
        
    Returns:
        bool: True if successful, False otherwise
    """
    store = get_customer_store()
    member_id = member_data.get("member_id")
    if not member_id:
        logger.warning("Attempted to add customer without member_id")
        return False
        
    store[member_id] = member_data
    logger.info(f"Added customer with member_id: {member_id}")
    return True

# Remove update_customer and delete_customer as they are unused 