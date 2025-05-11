"""
Call info store module.
Manages call context and information across requests.
"""
from . import get_store, CALL_INFO_STORE, store_operation
import logging

logger = logging.getLogger(__name__)

@store_operation
def get_call_info_store():
    """
    Get the call info store instance.
    
    Returns:
        dict: The call info store instance
    """
    return get_store(CALL_INFO_STORE)

@store_operation
def set_call_context(call_id, project_id):
    """
    Set call context information for a specific call.
    
    Args:
        call_id (str): The call ID
        project_id (str): The project ID associated with the call
    """
    store = get_call_info_store()
    if call_id not in store:
        store[call_id] = {}
    store[call_id]['context'] = {
        'project_id': project_id
    }
    logger.debug(f"Set context for call {call_id}: project_id={project_id}")

@store_operation
def get_call_context(call_id):
    """
    Get call context for a specific call.
    
    Args:
        call_id (str): The call ID
        
    Returns:
        dict or None: Call context if found, None otherwise
    """
    store = get_call_info_store()
    return store.get(call_id, {}).get('context')

@store_operation
def set_call_info(call_id, info_dict):
    """
    Set call information for a specific call.
    
    Args:
        call_id (str): The call ID
        info_dict (dict): Call information to store
    """
    store = get_call_info_store()
    if call_id not in store:
        store[call_id] = {}
    store[call_id]['info'] = info_dict
    logger.debug(f"Set info for call {call_id}")

@store_operation
def get_call_info(call_id):
    """
    Get call information for a specific call.
    
    Args:
        call_id (str): The call ID
        
    Returns:
        dict or None: Call information if found, None otherwise
    """
    store = get_call_info_store()
    return store.get(call_id, {}).get('info')

@store_operation
def remove_call(call_id):
    """
    Remove a call from the store.
    
    Args:
        call_id (str): The call ID to remove
        
    Returns:
        bool: True if removed, False if not found
    """
    store = get_call_info_store()
    if call_id in store:
        del store[call_id]
        logger.info(f"Removed call {call_id} from call info store")
        return True
    return False 