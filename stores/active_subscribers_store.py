# active_subscribers_store.py
# Global in-memory store for tracking online subscribers and their addresses, namespaced by project_id only
# Structure: {project_id: {subscriber_id: {address: str, online: bool, last_seen: datetime}}}

from datetime import datetime, UTC
from utils.session_utils import get_session_vars
from flask.sessions import SecureCookieSession
from typing import Dict, Any
import logging

active_subscribers: Dict[str, Dict[str, Dict[str, Any]]] = {}

def get_project_key(session_obj: SecureCookieSession) -> str:
    """
    Extracts the project_id from the session object for namespacing.
    Raises ValueError if session_obj is not a SecureCookieSession.
    Raises KeyError if required session variables are missing.
    """
    vars = get_session_vars(session_obj)
    project_id = vars.get('project_id')
    if project_id is None:
        raise KeyError('project_id must be present in session variables')
    return project_id

def set_active_subscriber(subscriber_id: str, address: str, session_obj: SecureCookieSession) -> None:
    """
    Mark a subscriber as active (online) and store their address, namespaced by session context.
    """
    key = get_project_key(session_obj)
    logging.info(f"[active_subscribers] Marking active: {subscriber_id} in {key}")
    if key not in active_subscribers:
        active_subscribers[key] = {}
    active_subscribers[key][subscriber_id] = {
        'address': address,
        'online': True,
        'last_seen': datetime.now(UTC)
    }

def set_inactive_subscriber(subscriber_id: str, session_obj: SecureCookieSession) -> None:
    """
    Mark a subscriber as inactive (offline) in the current session namespace.
    """
    key = get_project_key(session_obj)
    if key in active_subscribers and subscriber_id in active_subscribers[key]:
        active_subscribers[key][subscriber_id]['online'] = False
        active_subscribers[key][subscriber_id]['last_seen'] = datetime.now(UTC)

def get_active_subscribers(session_obj: SecureCookieSession) -> Dict[str, Dict[str, Any]]:
    """
    Return a dict of currently online subscribers for the session's namespace.
    """
    key = get_project_key(session_obj)
    if key not in active_subscribers:
        return {}
    return {k: v for k, v in active_subscribers[key].items() if v['online']}

def get_subscriber_address(subscriber_id: str, session_obj: SecureCookieSession) -> str | None:
    """
    Get the address of a subscriber in the current session namespace, or None if not found.
    """
    key = get_project_key(session_obj)
    return active_subscribers.get(key, {}).get(subscriber_id, {}).get('address')

def get_active_subscribers_by_project(project_id: str) -> Dict[str, Dict[str, Any]]:
    """
    Return a dict of currently online subscribers for the given project_id.
    """
    if project_id not in active_subscribers:
        return {}
    return {k: v for k, v in active_subscribers[project_id].items() if v['online']} 