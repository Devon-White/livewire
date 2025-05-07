from .. import api_bp
from flask import session, jsonify, current_app
from stores.user_store import get_user_store
import requests
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/api/create_sat', methods=['POST'])
def create_sat():
    email = session.get('user_email')
    logger.warning(f"create_sat called by user_email={email}")
    if not email or email not in get_user_store():
        logger.error("User not authenticated or not in user_store")
        return jsonify({'error': 'Not authenticated'}), 401
    project_id = session.get('sw_project_id')
    auth_token = session.get('sw_auth_token')
    space_name = session.get('sw_space_name')
    if not (project_id and auth_token and space_name):
        return jsonify({'error': 'SignalWire credentials missing from session. Please provide your credentials on the homepage.'}), 400
    api_url = f"https://{space_name}.signalwire.com/api/fabric/subscribers/tokens"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Basic {requests.auth._basic_auth_str(project_id, auth_token).split(" ")[1]}'
    }
    payload = {"reference": email}
    try:
        resp = requests.post(api_url, headers=headers, json=payload)
        logger.warning(f"SignalWire response: {resp.status_code} {resp.text}")
        if not resp.ok:
            return jsonify({'error': 'Failed to create token', 'details': resp.text}), 500
        data = resp.json()
        return jsonify({'token': data.get('token')})
    except Exception as e:
        logger.exception("Exception in create_sat")
        return jsonify({'error': str(e)}), 500 