from .. import api_bp
from flask import session, jsonify, current_app
from routes.html.signup import user_store
import requests
import os
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/api/create_sat', methods=['POST'])
def create_sat():
    email = session.get('user_email')
    logger.warning(f"create_sat called by user_email={email}")
    if not email or email not in user_store:
        logger.error("User not authenticated or not in user_store")
        return jsonify({'error': 'Not authenticated'}), 401
    SIGNALWIRE_SPACE = os.getenv('SIGNALWIRE_SPACE')
    api_url = f"https://{SIGNALWIRE_SPACE}.signalwire.com/api/fabric/subscribers/tokens"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': current_app.config['SIGNALWIRE_AUTH']
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