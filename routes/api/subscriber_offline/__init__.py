"""
Subscriber Offline API endpoint.
Marks a subscriber as offline/inactive when they close the dashboard.
"""
from routes.api import api_bp
from stores.active_subscribers_store import set_inactive_subscriber
from utils.api_utils import api_error, api_success
import logging
from flask import request

logger = logging.getLogger(__name__)

@api_bp.route('/api/subscriber_offline/<subscriber_id>', methods=['POST'])
def subscriber_offline(subscriber_id):
    """
    Mark a subscriber as offline/inactive.
    Called via beacon API when a subscriber closes the dashboard.
    
    Args:
        subscriber_id: The ID of the subscriber to mark as inactive
    """
    # Ensure request is JSON
    if not request.is_json:
        return api_error('This endpoint only accepts JSON data', 400)
        
    # Validate subscriber_id parameter
    if not subscriber_id or subscriber_id in ('null', 'undefined'):
        return api_error('No valid subscriber_id provided', 400)
    
    try:
        # Mark subscriber as inactive
        set_inactive_subscriber(subscriber_id)
        logger.info(f"Marked subscriber {subscriber_id} as inactive")
        return api_success(message="Subscriber marked as offline")
    except Exception as e:
        logger.exception(f"Error marking subscriber {subscriber_id} as inactive: {e}")
        return api_error(f"Failed to mark subscriber as inactive: {str(e)}", 500)
