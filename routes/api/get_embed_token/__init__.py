from .. import api_bp
from flask import jsonify, current_app
import requests
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/api/get_embed_token', methods=['GET'])
def get_embed_token():
    api_url = f"https://embeds.signalwire.com/api/fabric/embeds/tokens"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "token": current_app.config['C2C_TOKEN']
    }
    resp = requests.post(api_url, headers=headers, json=payload)
    logger.info(resp)
    if not resp.ok:
        return jsonify({"error": "Failed to get embeds token", "details": resp.text}), 500
    data = resp.json()
    logger.info(data)
    return jsonify(data) 