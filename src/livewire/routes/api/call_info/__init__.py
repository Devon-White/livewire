"""
Call Info API endpoint.
Provides information about active calls.
"""

import logging

from flask import request

from livewire.stores.call_info_store import get_call_info, get_call_info_store
from livewire.utils.api_utils import api_error, api_success, validate_json_request

from .. import api_bp

logger = logging.getLogger(__name__)


@api_bp.route("/api/call_info/<call_id>", methods=["GET"])
def call_info(call_id):
    """Get information about a specific call"""
    # Get call info from store
    info_data = get_call_info(call_id)
    if info_data:
        return api_success(info_data)
    else:
        return api_error("Call info not found", status_code=404, log_level="info")
