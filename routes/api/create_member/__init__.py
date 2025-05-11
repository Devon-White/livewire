"""
Create member API endpoint.
Handles creation of new members during calls and notifies AI agent.
"""
from .. import api_bp
from flask import request
import logging
import random
from stores.call_info_store import get_call_info_store
from stores.customer_store import get_customer_store, add_customer
from utils.api_utils import api_error, api_success, validate_json_request, validate_email
from utils.session_utils import get_session_vars, set_current_call_id, get_rest_client, get_current_call_id
from utils.signalwire_client import SignalWireAPIError

logger = logging.getLogger(__name__)

def get_current_call_id_from_sources():
    """Get the current call ID from various sources"""
    # Try from JSON data or session
    call_id = None
    
    # Try from JSON data
    if request.is_json:
        call_id = request.json.get('call_id')
    
    # Try from session using utility function
    if not call_id:
        call_id = get_current_call_id()
    
    # Try from call_info_store as last resort
    if not call_id:
        call_info_store = get_call_info_store()
        if call_info_store:
            call_id = next(iter(call_info_store.keys()), None)
            
    return call_id

def generate_unique_member_id():
    """Generate a unique member ID not already in the store"""
    store = get_customer_store()
    while True:
        member_id = f"M{random.randint(100000, 999999)}"
        if member_id not in store:
            return member_id

def format_member_data_prompt(member_data, member_id):
    """Format member data for AI prompt"""
    prompt_lines = [
        f"A new member has been created. Their member ID is: {member_id}",
        "They submitted the following information:",
        ""
    ]
    for k, v in member_data.items():
        prompt_lines.append(f"- {k}: {v}")
    return "\n".join(prompt_lines)

@api_bp.route('/api/create_member', methods=['POST'])
@validate_json_request(
    required_fields=['first_name', 'last_name', 'email', 'summary'],
    field_types={
        'first_name': str,
        'last_name': str, 
        'email': str,
        'summary': str
    },
    custom_validators={
        'email': validate_email
    }
)
def create_member():
    try:
        # 1. Get call_id
        call_id = get_current_call_id_from_sources()
        if not call_id:
            return api_error('No call_id found for create_member operation', log_level='error')
            
        # 2. Extract data from JSON
        form_data = request.json
        
        # 3. Generate unique member_id and add to store
        member_id = generate_unique_member_id()
        member_data = {
            'member_id': member_id,
            **form_data,
            'premium_member': True
        }
        add_customer(member_data)
        
        # 4. Format prompt for AI
        prompt = format_member_data_prompt(form_data, member_id)
        
        # 5. Send commands to SignalWire API using the client
        try:
            # Get client from session
            client = get_rest_client()
            if not client:
                return api_error("SignalWire client not initialized", 400)
            
            # Notify AI about new member (send message and unhold)
            client.notify_ai_about_new_member(call_id, prompt)
            
            # Store the call ID in the session
            set_current_call_id(call_id)
            
        except SignalWireAPIError as e:
            logger.exception(f'SignalWire API error: {e.message}')
            return api_error(
                'SignalWire API error', 
                500, 
                log_level='error',
                details={'message': e.message, 'status_code': e.status_code}
            )
            
        return api_success({'member_id': member_id}, 'Member created successfully')
        
    except Exception as e:
        logger.exception('Unexpected error in create_member')
        return api_error(
            'Unexpected error in create_member operation', 
            500, 
            log_level='error',
            details={'error': str(e)}
        )