"""
Widget Config API endpoint.
Provides configuration for the SignalWire call widget.
"""

import logging

from livewire.routes.api import api_bp
from livewire.utils.api_utils import (api_error, api_success,
                                      validate_json_request)
from livewire.utils.session_utils import get_rest_client, get_session_vars
from livewire.utils.signalwire_client import SignalWireAPIError

logger = logging.getLogger(__name__)


@api_bp.route("/api/widget_config", methods=["POST"])
@validate_json_request(
    required_fields=[],  # No required fields
    field_types={},      # No field type validation needed
)
def get_widget_config() -> tuple:
    """
    Get SignalWire widget configuration with guest token.

    Returns:
        tuple: (JSON response, HTTP status code)
    """
    # Get session variables
    session_vars = get_session_vars()
    swml_id = session_vars.get("swml_id")

    # Validate required data
    if not swml_id:
        logger.error("No SWML handler ID found in session")
        return api_error("No SWML handler ID found in session", 400)

    # Get client from session
    client = get_rest_client()
    if not client:
        return api_error("SignalWire client not initialized", 400)

    try:
        # Fetch addresses from handler
        addresses_response = client.get_handler_addresses(swml_id)
        destination = client.extract_audio_destination(addresses_response)

        if not destination:
            return api_error(
                "Failed to extract audio destination from SWML handler", 500
            )

        # Get address ID from the first address
        data = addresses_response.get("data", [])
        if not data:
            return api_error("No addresses found for SWML handler", 500)

        address_id = data[0].get("id")
        if not address_id:
            return api_error("No address ID found in SWML handler response", 500)

        # Request guest token
        token_response = client.create_guest_token(address_id)
        guest_token = token_response.get("token")

        if not guest_token:
            return api_error("Failed to get guest token from response", 500)

        # Return successful response with config
        return api_success({"guest_token": guest_token, "destination": destination})

    except SignalWireAPIError as e:
        logger.exception(f"SignalWire API error: {e.message}")
        return api_error(f"SignalWire API error: {e.message}", 500)

    except Exception as e:
        logger.exception(f"Unexpected error in get_widget_config: {str(e)}")
        return api_error(f"Unexpected error: {str(e)}", 500)
