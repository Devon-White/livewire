from flask import session, jsonify, request
import requests
from routes.api import api_bp
import base64
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/api/widget_config', methods=['POST'])
def get_widget_config():
    # Get SWML handler ID (used to fetch address)
    swml_id = session.get('swml_id')
    if not swml_id:
        logger.error('No SWML handler ID found in session.')
        return jsonify({'error': 'No SWML handler ID found in session.'}), 400

    # Get SignalWire credentials from session
    project_id = session.get('sw_project_id')
    auth_token = session.get('sw_auth_token')
    space_name = session.get('sw_space_name')
    if not (project_id and auth_token and space_name):
        logger.error(f"SignalWire credentials missing from session. project_id={project_id}, auth_token={'set' if auth_token else 'missing'}, space_name={space_name}")
        return jsonify({'error': 'SignalWire credentials missing from session.'}), 400

    # Prepare to fetch address info
    api_base = f"https://{space_name}.signalwire.com/api/fabric/resources/external_swml_handlers"
    auth = base64.b64encode(f"{project_id}:{auth_token}".encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Basic {auth}"
    }
    addresses_url = f"{api_base}/{swml_id}/addresses"
    logger.info(f"Fetching addresses for handler {swml_id} from {addresses_url}")
    try:
        addr_resp = requests.get(addresses_url, headers=headers)
        logger.info(f"Addresses response status: {addr_resp.status_code}")
        if not addr_resp.ok:
            logger.error(f"Failed to fetch addresses: {addr_resp.text}")
            return jsonify({'error': 'Failed to fetch handler addresses', 'details': addr_resp.text}), 500
        addr_data = addr_resp.json().get('data', [])
        if not addr_data:
            logger.error(f"No addresses found for handler {swml_id}")
            return jsonify({'error': 'No addresses found for handler'}), 500
        address_obj = addr_data[0]
        address_id = address_obj.get('id')
        channels = address_obj.get('channels') or address_obj.get('channel')
        if not channels or 'audio' not in channels:
            logger.error(f"No audio channel found in addresses for handler {swml_id}")
            return jsonify({'error': 'No audio channel found in handler addresses'}), 500
        destination = channels['audio'].split('?')[0]
        logger.info(f"Using address_id={address_id}, destination={destination}")
    except Exception as e:
        logger.exception(f"Exception while fetching handler addresses: {e}")
        return jsonify({'error': 'Exception while fetching handler addresses', 'details': str(e)}), 500

    # Now request guest token using the address_id
    guest_token_url = f"https://{space_name}.signalwire.com/api/fabric/guests/tokens"
    payload = {
        "allowed_addresses": [address_id]
    }
    logger.info(f"Requesting guest token with allowed_addresses={payload['allowed_addresses']}")
    try:
        resp = requests.post(guest_token_url, headers=headers, json=payload)
        logger.info(f"SignalWire guest token response status: {resp.status_code}")
        if not resp.ok:
            logger.error(f"Failed to get guest token: {resp.text}")
            return jsonify({"error": "Failed to get guest token", "details": resp.text}), 500
        data = resp.json()
        guest_token = data.get("token")
    except Exception as e:
        logger.exception(f"Exception while requesting guest token: {e}")
        return jsonify({"error": "Exception while requesting guest token", "details": str(e)}), 500

    # Optionally store destination in session for future fast access
    session['swml_destination'] = destination

    return jsonify({
        "guest_token": guest_token,
        "destination": destination
    }) 