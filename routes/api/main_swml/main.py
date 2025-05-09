from .. import api_bp
from flask import jsonify, current_app, request
from utils.swml_utils import load_swml_with_vars
from stores.call_info_store import set_call_context
import os
import logging

logger = logging.getLogger(__name__)

main_swml_file = os.path.join(os.path.dirname(__file__), "main_swml.yaml")

@api_bp.route('/api/swml', methods=['POST', 'GET'])
def swml():
    try:
        # Extract call context from the incoming request
        data = request.get_json(force=True, silent=True) or {}
        call = data.get('call', {})
        call_id = call.get('call_id')
        project_id = call.get('project_id')
        # space_name = call.get('space_id')  # No longer needed for context

        if call_id and project_id:
            set_call_context(call_id, project_id)
            logger.info(f"Set call context for call_id={call_id}: project_id={project_id}")

        public_url = current_app.config['PUBLIC_URL']
        swml_data = load_swml_with_vars(swml_file=main_swml_file, public_url=public_url)
        logger.info(f"Loaded SWML data for call_id={call_id}")
        return swml_data, 200
    except Exception as e:
        return jsonify({"error": f"Could not read SWML file: {e}"}), 500