"""
Call Status API endpoint.
Handles call status update webhooks from SignalWire.
"""
from .. import api_bp
from flask import request, jsonify
from stores.call_info_store import remove_call, get_call_info_store
from utils.api_utils import api_success, api_error, validate_json_request
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/api/call_status', methods=['POST'])
@validate_json_request()
def call_status():
    """Handle call status update webhooks"""
    try:
        # Extract call data from webhook payload
        data = request.json
        if not data:
            return api_error("Invalid webhook payload", 400)
        
        logger.info(f"Call status webhook received: {data}")
        
        # Extract segment_id from params - this is the consistent identifier across call legs
        params = data.get('params', {})
        segment_id = params.get('segment_id')

        # Get the call info store
        call_info_store = get_call_info_store()
        
        # Log all available keys in the store for debugging
        call_ids = list(call_info_store.keys())
        logger.debug(f"Available call IDs in store: {call_ids}")
        
        if segment_id:
            call_info = call_info_store.get(segment_id)
            if call_info:
                # Check if we should remove this call from the store
                connect_state = params.get('connect_state', '')
                                
                # Only remove call when it's in disconnected state
                if connect_state == 'disconnected':
                    success = remove_call(segment_id)
                    if success:
                        logger.info(f"Removed disconnected call {segment_id} from store")
            else:
                logger.debug(f"Call {segment_id} not found in store. Available IDs: {call_ids}")
        else:
            # Log the structure to help identify where the segment_id should be
            logger.warning(f"No segment_id found in params: {params}")
        
        return api_success(message="Call status processed")
        
    except Exception as e:
        logger.exception("Error processing call status webhook")
        return api_error(f"Error processing webhook: {str(e)}", 500) 