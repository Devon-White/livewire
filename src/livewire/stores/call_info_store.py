"""
Call info store module.
Manages call context and information across requests.
"""

import logging
from typing import Any, Dict

from . import CALL_INFO_STORE, get_store, store_operation

logger = logging.getLogger(__name__)


@store_operation
def get_call_info_store() -> Dict[str, Any]:
    """
    Get the call info store instance.

    Returns:
        Dict[str, Any]: The call info store instance
    """
    return get_store(CALL_INFO_STORE)


@store_operation
def set_call_context(call_id: str, project_id: str) -> bool:
    """
    Set the call context for a given call ID.

    Args:
        call_id (str): The call ID
        project_id (str): The project ID

    Returns:
        bool: True if successful
    """
    store = get_call_info_store()
    store[call_id] = {"project_id": project_id}
    logger.info(f"Set call context for call_id={call_id}, project_id={project_id}")
    return True


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
    return store.get(call_id)


@store_operation
def set_call_info(call_id: str, info: Dict[str, Any]) -> bool:
    """
    Set call information for a specific call ID. Merges with existing info if present.

    Args:
        call_id (str): The call ID
        info (Dict[str, Any]): Information to store

    Returns:
        bool: True if successful
    """
    store = get_call_info_store()
    if call_id in store and isinstance(store[call_id], dict):
        store[call_id].update(info)
    else:
        store[call_id] = info
    logger.info(f"Set call info for call_id={call_id}")
    return True


@store_operation
def get_call_info(call_id: str) -> Any:
    """
    Get call information for a specific call ID.

    Args:
        call_id (str): The call ID

    Returns:
        Any: Call information if found, None otherwise
    """
    store = get_call_info_store()
    return store.get(call_id)


@store_operation
def remove_call(call_id: str) -> bool:
    """
    Remove a call from the store by call ID.

    Args:
        call_id (str): The call ID

    Returns:
        bool: True if successful, False otherwise
    """
    store = get_call_info_store()
    if call_id in store:
        del store[call_id]
        logger.info(f"Removed call_id={call_id} from call info store")
        return True
    logger.warning(f"Attempted to remove non-existent call_id={call_id}")
    return False
