import logging
import os

from flask import current_app, jsonify, request

from livewire.stores.call_info_store import set_call_context
from livewire.utils.api_utils import api_error, validate_json_request
from livewire.utils.swml_utils import load_swml_with_vars

from .. import api_bp

logger = logging.getLogger(__name__)

main_swml_file = os.path.join(os.path.dirname(__file__), "main_swml.yaml")


@api_bp.route("/api/swml", methods=["POST", "GET"])
@validate_json_request(
    required_fields=[
        "call",
        "call.call_id",
        "call.project_id",
    ],  # 'call' is required for setting call context
    field_types={
        "call": dict,  # If 'call' is present, it should be a dictionary
        "call.call_id": str,  # Nested validation: call_id should be a string
        "call.project_id": str,  # Nested validation: project_id should be a string
    },
)
def swml():
    """
    Generate SWML for incoming calls and set call context.

    Returns:
        tuple: SWML JSON response or error
    """
    try:
        # Extract call context from the incoming request
        call = request.json["call"]  # Safe because of validation
        call_id = call["call_id"]
        project_id = call["project_id"]

        # Set call context for future reference
        set_call_context(call_id, project_id)
        logger.info(f"Set call context for call_id={call_id}, project_id={project_id}")

        # Generate SWML with variables
        public_url = current_app.config["PUBLIC_URL"]
        swml_data = load_swml_with_vars(swml_file=main_swml_file, public_url=public_url)
        logger.info(f"Generated SWML for call_id={call_id}")

        # Return SWML as a direct JSON response (special case for SignalWire's expected format)
        return jsonify(swml_data), 200

    except Exception as e:
        logger.exception(f"Error generating SWML: {e}")
        return api_error(f"Could not generate SWML: {str(e)}", 500)
