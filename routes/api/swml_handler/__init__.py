from flask import session, jsonify, request, current_app
import requests
import base64
from routes.api import api_bp
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/api/swml_handler', methods=['POST', 'PATCH'])
def swml_handler():
    # Gather credentials from session
    project_id = session.get('sw_project_id')
    auth_token = session.get('sw_auth_token')
    space_name = session.get('sw_space_name')
    public_url = current_app.config.get('PUBLIC_URL')
    if not (project_id and auth_token and space_name and public_url):
        return jsonify({'error': 'Missing credentials or public URL in session.'}), 400
    api_base = f"https://{space_name}.signalwire.com/api/fabric/resources/external_swml_handlers"
    auth = base64.b64encode(f"{project_id}:{auth_token}".encode()).decode()
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Basic {auth}'
    }
    payload = {
        "name": "LiveWire",
        "primary_request_url": f"{public_url.rstrip('/')}/api/swml"
    }
    swml_id = session.get('swml_id')

    def fetch_destination(swml_id):
        addresses_url = f"{api_base}/{swml_id}/addresses"
        resp = requests.get(addresses_url, headers=headers)
        if not resp.ok:
            logger.warning(f"Failed to fetch addresses for handler {swml_id}: {resp.text}")
            return None
        data = resp.json().get('data', [])
        if not data:
            logger.warning(f"No addresses found for handler {swml_id}")
            return None
        channels = data[0].get('channels') or data[0].get('channel')
        if not channels or 'audio' not in channels:
            logger.warning(f"No audio channel found in addresses for handler {swml_id}")
            return None
        audio_path = channels['audio']
        destination = audio_path.split('?')[0]
        return destination

    # Always try to update first if we have an ID
    if swml_id:
        url = f"{api_base}/{swml_id}"
        resp = requests.patch(url, headers=headers, json=payload)
        if resp.ok:
            destination = fetch_destination(swml_id)
            if destination:
                session['swml_destination'] = destination
            return jsonify({'id': swml_id, 'updated': True, 'destination': destination}), 200
        else:
            logger.warning(f"Failed to update SWML handler {swml_id}, will try to create new. Details: {resp.text}")
            # If PATCH fails, fall through to create new

    # If no ID or update failed, create new handler
    resp = requests.post(api_base, headers=headers, json=payload)
    if resp.ok:
        swml_id = resp.json().get('id')
        session['swml_id'] = swml_id
        destination = fetch_destination(swml_id)
        if destination:
            session['swml_destination'] = destination
        return jsonify({'id': swml_id, 'created': True, 'destination': destination}), 201
    else:
        # Clear session credentials on failure
        session.pop('sw_project_id', None)
        session.pop('sw_auth_token', None)
        session.pop('sw_space_name', None)
        session.pop('sw_credentials_ok', None)
        session.pop('swml_id', None)
        session.pop('swml_destination', None)
        # Return the actual status code from the API
        return jsonify({'error': 'Failed to create SWML handler', 'details': resp.text}), resp.status_code 