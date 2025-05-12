"""
SWML Handler API endpoint.
Creates or updates the SignalWire SWML handler.
"""

import logging

from flask import current_app, request

from livewire.routes.api import api_bp
from livewire.utils.api_utils import (api_error, api_success,
                                      validate_json_request)
from livewire.utils.session_utils import (get_session_vars,
                                          set_swml_handler_info)
from livewire.utils.signalwire_client import (SignalWireAPIError,
                                              SignalWireClient)

logger = logging.getLogger(__name__)


def create_or_update_handler(
    project_id: str,
    auth_token: str,
    space_name: str,
    public_url: str,
    swml_id: str = None,
) -> tuple:
    """
    Create or update a SWML handler using the SignalWireClient.

    Args:
        project_id (str): SignalWire project ID
        auth_token (str): SignalWire auth token
        space_name (str): SignalWire space name
        public_url (str): Public URL for the handler
        swml_id (str, optional): Optional existing handler ID

    Returns:
        tuple: (handler_id, destination, created_flag) or (None, None, None) on error
    """
    client = SignalWireClient(project_id, auth_token, space_name)
    request_url = f"{public_url.rstrip('/')}/api/swml"

    try:
        # Try to update first if we have an ID
        if swml_id:
            try:
                client.update_swml_handler(swml_id, "LiveWire", request_url)
                addresses = client.get_handler_addresses(swml_id)
                destination = client.extract_audio_destination(addresses)
                return swml_id, destination, False  # Updated
            except SignalWireAPIError as e:
                logger.warning(
                    f"Failed to update SWML handler {swml_id}, will try to create new. Details: {e.message}"
                )
                # Fall through to create

        # Create new handler
        response = client.create_swml_handler("LiveWire", request_url)
        new_swml_id = response.get("id")
        addresses = client.get_handler_addresses(new_swml_id)
        destination = client.extract_audio_destination(addresses)
        return new_swml_id, destination, True  # Created

    except SignalWireAPIError as e:
        logger.error(f"SignalWire API error: {e.message}")
        return None, None, None


@api_bp.route("/api/swml_handler", methods=["POST", "PATCH"])
@validate_json_request(
    required_fields=[],  # No required fields in the request
    field_types={},  # No field type validation needed
)
def swml_handler() -> tuple:
    """
    Create or update the SWML handler.

    Returns:
        tuple: (JSON response, HTTP status code)
    """
    # Get session variables and app config
    session_vars = get_session_vars()
    project_id = session_vars.get("project_id")
    auth_token = session_vars.get("auth_token")
    space_name = session_vars.get("space_name")
    swml_id = session_vars.get("swml_id")
    public_url = current_app.config.get("PUBLIC_URL")

    # Validate required data
    if not (project_id and auth_token and space_name and public_url):
        missing = []
        if not project_id:
            missing.append("project_id")
        if not auth_token:
            missing.append("auth_token")
        if not space_name:
            missing.append("space_name")
        if not public_url:
            missing.append("public_url")
        return api_error(
            f'Missing credentials or public URL: {", ".join(missing)}', 400
        )

    # Create or update handler
    handler_id, destination, created = create_or_update_handler(
        project_id, auth_token, space_name, public_url, swml_id
    )

    if not handler_id:
        # Don't clear session variables, just log the error
        logger.error(
            f"Failed to create/update SWML handler - project_id: {project_id}, space_name: {space_name}"
        )
        return api_error("Failed to create or update SWML handler", 500)

    # Store handler ID and destination in session using the utility function
    set_swml_handler_info(handler_id, destination)

    # Return successful response
    return api_success(
        {
            "id": handler_id,
            "created": created,
            "updated": not created,
            "destination": destination,
        },
        status_code=201 if created else 200,
    )
