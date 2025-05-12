"""
Call Status API endpoint.
Handles call status update webhooks from SignalWire.
"""

import logging

from flask import jsonify, request

from livewire.stores.call_info_store import get_call_info_store, remove_call
from livewire.utils.api_utils import (api_error, api_success,
                                      validate_json_request)

from .. import api_bp

logger = logging.getLogger(__name__)


@api_bp.route("/api/call_status", methods=["POST"])
@validate_json_request(
    required_fields=["params"],  # Only params is guaranteed
    field_types={
        "params": dict           # Params should be a dictionary
    }
)
def call_status():
    """Handle call status update webhooks from SignalWire"""
    try:
        # Get the params object, which is validated
        params = request.json["params"]
        
        # segment_id may not always be present in all webhook types
        segment_id = params.get("segment_id")
        connect_state = params.get("connect_state", "")

        logger.info(f"Call status webhook received with params: {params}")

        # Process only if segment_id exists
        if segment_id:
            # Get the call info store
            call_info_store = get_call_info_store()
            call_ids = list(call_info_store.keys())
            
            call_info = call_info_store.get(segment_id)
            if call_info:
                # Only remove call when it's in disconnected state
                if connect_state == "disconnected":
                    success = remove_call(segment_id)
                    if success:
                        logger.info(f"Removed disconnected call {segment_id} from store")
            else:
                logger.debug(f"Call {segment_id} not found in store. Available IDs: {call_ids}")
        else:
            logger.info("Webhook received without segment_id - this may be normal for certain event types")

        return api_success(message="Call status processed")

    except Exception as e:
        logger.exception("Error processing call status webhook")
        return api_error(f"Error processing webhook: {str(e)}", 500)
