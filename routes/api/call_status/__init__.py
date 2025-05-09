from .. import api_bp
from flask import request, jsonify
from stores.call_info_store import get_call_info_store
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/api/call_status', methods=['POST'])
def call_status():
    data = request.json
    params = data.get('params', {})
    peer_call_id = params.get('peer', {}).get('call_id')

    if peer_call_id:
      get_call_info_store().pop(peer_call_id, None)
    return jsonify({'success': True}) 