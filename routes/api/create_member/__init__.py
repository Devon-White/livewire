from .. import api_bp
from flask import jsonify, request, session
import requests
import logging
from stores.call_info_store import get_call_info_store, set_call_context
from stores.customer_store import get_customer_store
import random

logger = logging.getLogger(__name__)

@api_bp.route('/api/create_member', methods=['POST'])
def create_member():
    # 1. Extract form data
    form = request.form
    form_data = {k: v for k, v in form.items()}

    # 2. Get call_id (try from form, session, or call_info_store)
    call_id = form.get('call_id') or session.get('current_call_id')
    if not call_id:
        # Try to get the most recent call_id from call_info_store
        call_info_store = get_call_info_store()
        if call_info_store:
            call_id = next(iter(call_info_store.keys()), None)
    if not call_id:
        logger.error('No call_id found for create_member inject/unhold')
        return jsonify({'error': 'No call_id found'}), 400

    # 3. Generate a unique member_id
    def generate_member_id():
        store = get_customer_store()
        while True:
            mid = f"M{random.randint(100000, 999999)}"
            if mid not in store:
                return mid
    member_id = generate_member_id()

    # 4. Add new member to the global store
    customer_store = get_customer_store()
    customer_store[member_id] = {
        'member_id': member_id,
        **form_data,
        'premium_member': True
    }

    # 5. Format prompt for AI (include member_id)
    prompt_lines = [
        f"A new member has been created. Their member ID is: {member_id}",
        "They submitted the following information:",
        ""
    ]
    for k, v in form_data.items():
        prompt_lines.append(f"- {k}: {v}")
    prompt = "\n".join(prompt_lines)

    # 6. Prepare API credentials
    project_id = session.get('sw_project_id')
    auth_token = session.get('sw_auth_token')
    space_name = session.get('sw_space_name')
    if not (project_id and auth_token and space_name):
        logger.error('SignalWire credentials missing from session')
        return jsonify({'error': 'SignalWire credentials missing from session'}), 400
    api_url = f"https://{space_name}.signalwire.com/api/calling/calls"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Basic {requests.auth._basic_auth_str(project_id, auth_token).split(" ")[1]}'
    }

    # 7. Inject message to agent (calling.ai_message)
    inject_payload = {
        "id": call_id,
        "command": "calling.ai_message",
        "params": {
            "role": "system",
            "message_text": prompt
        }
    }
    try:
        inject_resp = requests.post(api_url, headers=headers, json=inject_payload)
        logger.info(f"Inject response: status={inject_resp.status_code}")
        inject_resp.raise_for_status()
    except Exception as e:
        logger.exception('Failed to inject message to agent')
        return jsonify({'error': 'Failed to inject message', 'details': str(e)}), 500

    # 8. Unhold the agent (calling.ai_unhold)
    unhold_payload = {
        "id": call_id,
        "command": "calling.ai_unhold",
        "params": {}
    }
    try:
        unhold_resp = requests.post(api_url, headers=headers, json=unhold_payload)
        logger.info(f"Unhold response: status={unhold_resp.status_code}")
        unhold_resp.raise_for_status()
    except Exception as e:
        logger.exception('Failed to unhold agent')
        return jsonify({'error': 'Failed to unhold agent', 'details': str(e)}), 500

    return jsonify({'success': True, 'member_id': member_id})