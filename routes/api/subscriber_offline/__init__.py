from flask import jsonify, session
from stores.active_subscribers_store import set_inactive_subscriber

from routes.api import api_bp

@api_bp.route('/api/subscriber_offline/<subscriber_id>', methods=['POST'])
def subscriber_offline(subscriber_id):
    if not subscriber_id or subscriber_id == 'null' or subscriber_id == 'undefined':
        return jsonify({'success': False, 'error': 'No valid subscriber_id provided'}), 400
    try:
        set_inactive_subscriber(subscriber_id, session)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
