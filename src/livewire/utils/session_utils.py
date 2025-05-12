"""
Session utility functions for the LiveWire demo app.
Provides consistent access to session variables and common operations.
"""

import logging
from typing import Any, Dict, Optional

from flask import session as flask_session

from livewire.utils.signalwire_client import SignalWireClient

logger = logging.getLogger(__name__)

# Session key constants
SW_PROJECT_ID: str = "sw_project_id"
SW_AUTH_TOKEN: str = "sw_auth_token"
SW_SPACE_NAME: str = "sw_space_name"
SW_CREDENTIALS_OK: str = "sw_credentials_ok"
SUBSCRIBER_OK: str = "subscriber_ok"
SWML_ID: str = "swml_id"
SWML_DESTINATION: str = "swml_destination"
CURRENT_CALL_ID: str = "current_call_id"
USER_EMAIL: str = "user_email"


def get_session_vars(session_obj: Optional[dict] = None) -> Dict[str, Any]:
    """
    Returns a dict of all relevant session variables for namespacing data.

    Args:
        session_obj (Optional[dict]): Optional session object to use instead of flask.session

    Returns:
        Dict[str, Any]: Dictionary of session variables
    """
    s = session_obj if session_obj is not None else flask_session

    # Always log what's in the session for debugging
    logger.debug(f"Session keys: {list(s.keys())}")
    logger.debug(f"Project ID: {s.get(SW_PROJECT_ID)}")
    logger.debug(f"Space Name: {s.get(SW_SPACE_NAME)}")
    logger.debug(f"Credentials OK: {s.get(SW_CREDENTIALS_OK)}")

    return {
        "project_id": s.get(SW_PROJECT_ID),
        "auth_token": s.get(SW_AUTH_TOKEN),
        "space_name": s.get(SW_SPACE_NAME),
        "swml_id": s.get(SWML_ID),
        "swml_destination": s.get(SWML_DESTINATION),
        "current_call_id": s.get(CURRENT_CALL_ID),
        "user_email": s.get(USER_EMAIL),
    }


def has_sw_credentials() -> bool:
    """
    Check if SignalWire credentials are present in the session.
    Always verifies the actual credentials, not just the flag.

    Returns:
        bool: True if all credentials are present, False otherwise
    """
    # Check both the flag AND all credential values
    flag_set = bool(flask_session.get(SW_CREDENTIALS_OK))
    project_id = bool(flask_session.get(SW_PROJECT_ID))
    auth_token = bool(flask_session.get(SW_AUTH_TOKEN))
    space_name = bool(flask_session.get(SW_SPACE_NAME))

    # Log the state for debugging
    logger.debug(
        f"Credential check: flag={flag_set}, project={project_id}, auth={auth_token}, space={space_name}"
    )

    # All must be present
    return flag_set and project_id and auth_token and space_name


def is_subscriber_logged_in() -> bool:
    """
    Check if user is logged in as a subscriber.
    Verifies both the flag and the email.

    Returns:
        bool: True if subscriber is logged in, False otherwise
    """
    flag_set = bool(flask_session.get(SUBSCRIBER_OK))
    has_email = bool(flask_session.get(USER_EMAIL))

    logger.debug(f"Subscriber check: flag={flag_set}, email={has_email}")

    return flag_set and has_email


def get_subscriber_login_status() -> bool:
    """
    Get the subscriber login status flag from the session.

    Returns:
        bool: True if subscriber_ok flag is set, False otherwise
    """
    status = bool(flask_session.get(SUBSCRIBER_OK, False))
    logger.debug(f"Getting subscriber login status: {status}")
    return status


def set_sw_credentials(project_id: str, auth_token: str, space_name: str) -> bool:
    """
    Store SignalWire credentials in the session.
    All values must be non-empty.

    Args:
        project_id (str): SignalWire project ID
        auth_token (str): SignalWire auth token
        space_name (str): SignalWire space name

    Returns:
        bool: True if successful, False otherwise
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


def get_rest_client() -> Optional[SignalWireClient]:
    """
    Create a SignalWireClient instance using credentials from the session.
    The client is created fresh each time to avoid serialization issues.

    Returns:
        Optional[SignalWireClient]: The client instance or None if credentials are missing
    """
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


def set_subscriber_login(email: str) -> bool:
    """
    Mark user as logged in as a subscriber.

    Args:
        email (str): Subscriber's email address

    Returns:
        bool: True if successful, False otherwise
    """
    if not email:
        logger.warning("Attempted to set empty subscriber email")
        return False

    flask_session[USER_EMAIL] = email
    flask_session[SUBSCRIBER_OK] = True

    logger.info(f"Set subscriber login for {email}")
    return True


def clear_subscriber_login() -> bool:
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


def set_swml_handler_info(handler_id: str, destination: Optional[str] = None) -> bool:
    """
    Store SWML handler information in the session.

    Args:
        handler_id (str): The SWML handler ID
        destination (Optional[str]): Optional destination URL

    Returns:
        bool: True if successful, False otherwise
    """
    if not handler_id:
        logger.warning("Attempted to set empty SWML handler ID")
        return False

    flask_session[SWML_ID] = handler_id
    if destination:
        flask_session[SWML_DESTINATION] = destination

    logger.info(
        f"Set SWML handler info: ID={handler_id}, destination={destination or 'None'}"
    )
    return True


def set_current_call_id(call_id: str) -> bool:
    """
    Store the current call ID in the session.

    Args:
        call_id (str): Active call ID

    Returns:
        bool: True if successful, False otherwise
    """
    if not call_id:
        logger.warning("Attempted to set empty call ID")
        return False

    flask_session[CURRENT_CALL_ID] = call_id
    logger.info(f"Set current call ID: {call_id}")
    return True


def get_current_call_id() -> Optional[str]:
    """
    Get the current call ID from the session.

    Returns:
        Optional[str]: The current call ID or None if not set
    """
    call_id = flask_session.get(CURRENT_CALL_ID)
    return call_id


def clear_session() -> bool:
    """
    Clear all session data and ensure nothing remains.

    Returns:
        bool: True if successful
    """
    # Log what we're clearing
    logger.info(f"Clearing session with keys: {list(flask_session.keys())}")

    # Clear everything
    flask_session.clear()

    # Verify it's actually cleared
    logger.info(f"Session after clearing: {list(flask_session.keys())}")

    return True
