"""
Call Info API endpoint.
Provides information about active calls.
"""
from .. import api_bp
from flask import request
from stores.call_info_store import get_call_info_store, get_call_info
from utils.api_utils import api_error, api_success
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/api/call_info/<call_id>', methods=['GET'])
def call_info(call_id):
    """Get information about a specific call"""
    if request.method != 'GET':
        return api_error('Method not allowed', status_code=405)
    
    # Get call info from store
    info_data = get_call_info(call_id)
    if info_data:
        return api_success(info_data)
    else:
        return api_error('Call info not found', status_code=404, log_level='info') 