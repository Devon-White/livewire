from .. import api_bp
from flask import jsonify, request
from stores.call_info_store import get_call_info_store
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/api/call_info/<call_id>', methods=['GET'])
def call_info(call_id):
    if request.method == 'GET':
        # logger.info(get_call_info_store())  # Remove this log
        info = get_call_info_store().get(call_id)
        if info and 'info' in info:
            return jsonify(info['info']), 200
        else:
            return jsonify({'error': 'Call info not found'}), 404
    else:
        return jsonify({'error': 'Method not allowed'}), 405 